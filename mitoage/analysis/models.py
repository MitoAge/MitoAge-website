import collections
import time

from django.db import connection
from django.db import models
from django.db.models.aggregates import Avg, Max, Min, StdDev
import simplejson

from mitoage.taxonomy.models import TaxonomySpecies, TaxonomyClass, \
    TaxonomyOrder, TaxonomyFamily


def median_value(queryset,term):
    count = queryset.count()
    if count==0:
        return "-"
    return queryset.values_list(term, flat=True).order_by(term)[int(round(count/2))]

 
class StatsCache(models.Model):
    TAXON_TYPES = ( (1, 'All species'), (2, 'Class'), (3, 'Order'), (4, 'Family'), )
    TAXON_DICT = {1:'All species', 2:'Class', 3:'Order', 4:'Family'}

    class Meta:
        unique_together = ('group_type', 'taxon_id', 'group_section')

    # unique key
    group_type = models.IntegerField("Type of group", max_length=1, choices = TAXON_TYPES, default=1)
    taxon_id = models.IntegerField("Taxon ID", max_length=11)
    group_section = models.CharField("Section of mtDNA", max_length=20)

    # data
    group_size = models.IntegerField("Size of group", max_length=5)
    stats_dump = models.TextField("Cached stats")
    
    def dump_stats(self, group_type, taxon_id, section, stats):
        (self.group_section, self.group_size, self.group_type, self.taxon_id) = (section, stats.group_size, group_type, taxon_id)
        self.stats_dump = simplejson.dumps([stats.min, stats.max, stats.mean, stats.stdev, stats.median, stats.coef_var], use_decimal=True)

    def get_group_name(self):
        if self.group_type==1:
            return "All species"
        elif self.group_type==2:
            try:
                return TaxonomyClass.objects.get(id=self.taxon_id).name
            except TaxonomyClass.DoesNotExist:
                return "(Class not found)"
        elif self.group_type==3:
            try:
                return TaxonomyOrder.objects.get(id=self.taxon_id).name
            except TaxonomyOrder.DoesNotExist:
                return "(Order not found)"
        elif self.group_type==4:
            try:
                return TaxonomyFamily.objects.get(id=self.taxon_id).name
            except TaxonomyFamily.DoesNotExist:
                return "(Family not found)"
        return "(Custom species set)"

    def __unicode__(self):
        return u'%s stats for %s%s' % (self.group_section, StatsCache.TAXON_DICT.get(self.group_type,"").lower(), (" %s" % self.get_group_name() if (self.group_type in [2,3,4]) else "") ) 


class BaseCompositionStats():
    def __init__(self, species, section, taxon_type="Custom", taxon_object=None):
        self.section = section
        start = time.time()
        
        if taxon_type!="Custom" and species.count()>5:
            group_type = {"":1, "class":2, "order":3, "family":4}[taxon_type] if taxon_type else 1
            taxon_id = taxon_object.pk if taxon_object else 0
            try:
                cache = StatsCache.objects.get(group_type=group_type, taxon_id=taxon_id, group_section=section)
                self.group_size = cache.group_size
                self.min, self.max, self.mean, self.stdev, self.median, self.coef_var = simplejson.loads(cache.stats_dump) 
                
            except StatsCache.DoesNotExist:
                # no cache found, computing and saving
                self.compute_stats2(species, section)
                cache = StatsCache()
                cache.dump_stats(group_type, taxon_id, section, self)
                cache.save()
            except StatsCache.MultipleObjectsReturned:
                # what to do if multiple caches have been returned?
                pass
        else:
            self.compute_stats2(species, section)
            
        end = time.time()
        self.elapsed_time = end - start        


    def compute_stats2(self, species, section):
        section_translation = {'total_mtDNA':'total_mtDNA', 'total_pc_mtDNA':'total_mtDNA_pc', 'd_loop_mtDNA':'d_loop', 
                               'total_tRNA_mtDNA':'total_tRNA', 'total_rRNA_mtDNA':'total_rRNA', 'atp6':'atp6', 'atp8':'atp8', 
                               'cox1':'cox1', 'cox2':'cox2', 'cox3':'cox3', 'cytb':'cytb', 'nd1':'nd1', 'nd2':'nd2', 'nd3':'nd3', 
                               'nd4':'nd4', 'nd4l':'nd4l', 'nd5':'nd5', 'nd6':'nd6', 'rRNA_12S':'rRNA_12S', 'rRNA_16S':'rRNA_16S'}.get(section, 'total_mtDNA')
        section_prefix = "bc_%s_" % section_translation

        self.min, self.max, self.mean, self.stdev, self.median, self.coef_var = ({}, {}, {}, {}, {}, {})

        kwargs1 = { ('%ssize__isnull' % section_prefix): 'True', }
        kwargs2 = { ('%ssize__exact' % section_prefix): '0', }
        mitoage_entries = MitoAgeEntry.objects.filter(species__pk__in=species).exclude(**kwargs1).exclude(**kwargs2)
        self.group_size = mitoage_entries.count()
        
        if self.group_size <= 5:
            self.compositions = [ (x.species, x.get_base_composition(section)) for x in mitoage_entries ]
            return 

        self.compute_stats_for("g", section_prefix, mitoage_entries) 
        self.compute_stats_for("c", section_prefix, mitoage_entries) 
        self.compute_stats_for("a", section_prefix, mitoage_entries) 
        self.compute_stats_for("t", section_prefix, mitoage_entries) 
        self.compute_stats_for("lifespan", "species__", mitoage_entries)
        
        cursor = connection.cursor()
        fake_query = str(mitoage_entries.annotate(x=Min("%sg" % section_prefix)).query)
        from_query = fake_query[fake_query.find('FROM'):fake_query.find('GROUP BY')]

        self.additional_column = '(("analysis_mitoageentry"."%sg" + "analysis_mitoageentry"."%sc")*100.0/"analysis_mitoageentry"."%ssize")' % (section_prefix, section_prefix, section_prefix)
        self.compute_stats_through_direct_queries(cursor, "gc", from_query, self.additional_column)
        
        self.additional_column = '(("analysis_mitoageentry"."%sa" + "analysis_mitoageentry"."%st")*100.0/"analysis_mitoageentry"."%ssize")' % (section_prefix, section_prefix, section_prefix)
        self.compute_stats_through_direct_queries(cursor, "at", from_query, self.additional_column)



    def compute_stats_through_direct_queries(self, cursor, field_name, from_query, column):
        cursor.execute('SELECT min%s %s' % (column, from_query) )
        self.min[field_name] = cursor.fetchone()[0]
        cursor.execute('SELECT max%s %s' % (column, from_query) )
        self.max[field_name] = cursor.fetchone()[0]
        cursor.execute('SELECT avg%s %s' % (column, from_query) )
        self.mean[field_name] = cursor.fetchone()[0]
        cursor.execute('SELECT stddev%s %s' % (column, from_query) )
        self.stdev[field_name] = cursor.fetchone()[0]

        self.median[field_name] = self.compute_median_with_direct_queries(cursor, from_query, column)[0]
        self.compute_coef_of_variance(field_name)

    
    def compute_median_with_direct_queries(self, cursor, from_query, column):
        cursor.execute('SELECT count%s %s' % (column, from_query) )
        count = cursor.fetchone()[0]
        if count==0:
            return "-"
        query = 'SELECT %s %s ORDER BY %s' % (column, from_query, column)
        cursor.execute(query)
        return cursor.fetchall()[int(round(count/2))]

    def compute_coef_of_variance(self, field_name):    
        if self.stdev[field_name]:
            self.coef_var[field_name] = self.stdev[field_name] / self.mean[field_name]
        else:
            self.coef_var[field_name] = None

    
    def compute_stats_for(self, field_name, section_prefix, entries):
        full_field_name = section_prefix + field_name
        results = entries.aggregate(average_value = Avg(full_field_name), stdev_value = StdDev(full_field_name), max_value = Max(full_field_name), min_value = Min(full_field_name))
        self.min[field_name] = results['min_value']
        self.max[field_name] = results['max_value']
        self.mean[field_name] = results['average_value']
        self.stdev[field_name] = results['stdev_value']
        self.median[field_name] = median_value(entries,full_field_name)
        self.compute_coef_of_variance(field_name)
    
    
    def to_string(self):
        return "n:%s, min:%s, max:%s, mean:%s, stdev:%s, median:%s" % (self.group_size, self.min, self.max, self.mean, self.stdev, self.median)
        

class BaseComposition():
    def __init__(self, size, g, c, a, t, others):
        self.size = size
        self.g = g
        self.c = c
        self.a = a
        self.t = t
        self.others = others

    def gc(self):
        return self.g + self.c

    def at(self):
        return self.a + self.t

    def is_same(self, other):
        return self.size==other.size and self.g==other.g and self.c==other.c and self.a==other.a and self.t==other.t and self.others==other.others 

    def is_empty(self):
        return self.is_full_of_0() or self.size==None and self.g==None and self.c==None and self.a==None and self.t==None and self.others==None 

    def is_full_of_0(self):
        return self.size==0 and self.g==0 and self.c==0 and self.a==0 and self.t==0 and self.others==0 

    def to_raw_data(self):
        return (self.size, self.g, self.c, self.a, self.t, self.others)
    
    def to_string(self):
        return "[G:%s;C:%s;A:%s;T:%s;O:%s] - size: %s bp" % (self.g, self.c, self.a, self.t, self.others, self.size)

    @staticmethod
    def get_bc_sections():
        return ['total_mtDNA', 'total_pc_mtDNA', 'd_loop_mtDNA', 'total_tRNA_mtDNA', 'total_rRNA_mtDNA', 'atp6', 'atp8', 'cox1', 'cox2', 'cox3', 'cytb', 'nd1', 'nd2', 'nd3', 'nd4', 'nd4l', 'nd5', 'nd6', 'rRNA_12S', 'rRNA_16S']

    @staticmethod
    def get_nice_title(key):
        return {
            'total_mtDNA': "Total mtDNA",
            'total_pc_mtDNA': "Total protein-coding genes",
            'd_loop_mtDNA': "D-loop",
            'total_tRNA_mtDNA': "Total tRNA-coding genes",
            'total_rRNA_mtDNA': "Total rRNA-coding genes",
            'atp6': "ATP6",
            'atp8': "ATP8",
            'cox1': "COX1",
            'cox2': "COX2",
            'cox3': "COX3",
            'cytb': "CYTB",
            'nd1': "ND1",
            'nd2': "ND2",
            'nd3': "ND3",
            'nd4': "ND4",
            'nd4l': "ND4L",
            'nd5': "ND5",
            'nd6': "ND6",
            'rRNA_12S': "12S rRNA gene",
            'rRNA_16S': "16S rRNA gene",
        }.get(key, "No title")



class AminoAcid():

    def __init__(self, letter):
        self.letter = letter
        self.symbol = AminoAcid.get_aa_symbol(letter)
        self.name = AminoAcid.get_aa_name(letter)
    
    @staticmethod
    def get_aa_name(aa_letter):
        return {"G":"Glycine", "A":"Alanine", "S":"Serine", "T":"Threonine", "C":"Cysteine", "V":"Valine", "L":"Leucine", "I":"Isoleucine", 
                "M":"Methionine", "P":"Proline", "F":"Phenylalanine", "Y":"Tyrosine", "W":"Tryptophan", "D":"Aspartic acid", 
                "E":"Glutamic acid", "N":"Asparagine", "Q":"Glutamine", "H":"Histidine", "K":"Lysine", "R":"Arginine"}.get(aa_letter, "N/A")

    @staticmethod
    def get_aa_symbol(aa_letter):
        return {"G":"Gly", "A":"Ala", "S":"Ser", "T":"Thr", "C":"Cys", "V":"Val", "L":"Leu", "I":"Ile", "M":"Met", "P":"Pro", 
                "F":"Phe", "Y":"Tyr", "W":"Trp", "D":"Asp", "E":"Glu", "N":"Asn", "Q":"Gln", "H":"His", "K":"Lys", "R":"Arg"}.get(aa_letter, "N/A")

    @staticmethod
    def get_amino_acids():
        return [AminoAcid("G"), AminoAcid("A"), AminoAcid("S"), AminoAcid("T"), AminoAcid("C"), AminoAcid("V"), AminoAcid("L"), AminoAcid("I"), 
                AminoAcid("M"), AminoAcid("P"), AminoAcid("F"), AminoAcid("Y"), AminoAcid("W"), AminoAcid("D"), AminoAcid("E"), AminoAcid("N"), 
                AminoAcid("Q"), AminoAcid("H"), AminoAcid("K"), AminoAcid("R")]


class CodonUsage(models.Model):

    @staticmethod
    def get_cu_sections():
        return ['total_pc_mtDNA', 'atp6', 'atp8', 'cox1', 'cox2', 'cox3', 'cytb', 'nd1', 'nd2', 'nd3', 'nd4', 'nd4l', 'nd5', 'nd6']

    @staticmethod
    def get_nice_title(key):
        return {
            'total_pc_mtDNA': "Total protein-coding genes",
            'atp6': "ATP6",
            'atp8': "ATP8",
            'cox1': "COX1",
            'cox2': "COX2",
            'cox3': "COX3",
            'cytb': "CYTB",
            'nd1': "ND1",
            'nd2': "ND2",
            'nd3': "ND3",
            'nd4': "ND4",
            'nd4l': "ND4L",
            'nd5': "ND5",
            'nd6': "ND6",
        }.get(key, "No title")

    cu_protein_coding_entry = models.OneToOneField("MitoAgeEntry", related_name = "protein_coding_codon_usage", blank=True, null = True)
    cu_atp6_entry = models.OneToOneField("MitoAgeEntry", related_name = "atp6_codon_usage", blank=True, null = True)
    cu_atp8_entry = models.OneToOneField("MitoAgeEntry", related_name = "atp8_codon_usage", blank=True, null = True)
    cu_cox1_entry = models.OneToOneField("MitoAgeEntry", related_name = "cox1_codon_usage", blank=True, null = True)
    cu_cox2_entry = models.OneToOneField("MitoAgeEntry", related_name = "cox2_codon_usage", blank=True, null = True)
    cu_cox3_entry = models.OneToOneField("MitoAgeEntry", related_name = "cox3_codon_usage", blank=True, null = True)
    cu_cytb_entry = models.OneToOneField("MitoAgeEntry", related_name = "cytb_codon_usage", blank=True, null = True)
    cu_nd1_entry = models.OneToOneField("MitoAgeEntry", related_name = "nd1_codon_usage", blank=True, null = True)
    cu_nd2_entry = models.OneToOneField("MitoAgeEntry", related_name = "nd2_codon_usage", blank=True, null = True)
    cu_nd3_entry = models.OneToOneField("MitoAgeEntry", related_name = "nd3_codon_usage", blank=True, null = True)
    cu_nd4_entry = models.OneToOneField("MitoAgeEntry", related_name = "nd4_codon_usage", blank=True, null = True)
    cu_nd4l_entry = models.OneToOneField("MitoAgeEntry", related_name = "nd4l_codon_usage", blank=True, null = True)
    cu_nd5_entry = models.OneToOneField("MitoAgeEntry", related_name = "nd5_codon_usage", blank=True, null = True)
    cu_nd6_entry = models.OneToOneField("MitoAgeEntry", related_name = "nd6_codon_usage", blank=True, null = True)
    
    size = models.IntegerField("Size", max_length=11, blank=True, null = True)
    aa = models.TextField("Amino acids")

    AUU = models.IntegerField(max_length=11, blank=True, null = True)
    AUC = models.IntegerField(max_length=11, blank=True, null = True)
    AUA = models.IntegerField(max_length=11, blank=True, null = True)
    CUU = models.IntegerField(max_length=11, blank=True, null = True)
    CUC = models.IntegerField(max_length=11, blank=True, null = True)
    CUA = models.IntegerField(max_length=11, blank=True, null = True)
    CUG = models.IntegerField(max_length=11, blank=True, null = True)
    UUA = models.IntegerField(max_length=11, blank=True, null = True)
    CAA = models.IntegerField(max_length=11, blank=True, null = True)
    CAG = models.IntegerField(max_length=11, blank=True, null = True)
    GUU = models.IntegerField(max_length=11, blank=True, null = True)
    GUC = models.IntegerField(max_length=11, blank=True, null = True)
    GUA = models.IntegerField(max_length=11, blank=True, null = True)
    GUG = models.IntegerField(max_length=11, blank=True, null = True)
    UUU = models.IntegerField(max_length=11, blank=True, null = True)
    UUC = models.IntegerField(max_length=11, blank=True, null = True)    
    AUG = models.IntegerField(max_length=11, blank=True, null = True)
    UGU = models.IntegerField(max_length=11, blank=True, null = True)
    UGC = models.IntegerField(max_length=11, blank=True, null = True)
    GCU = models.IntegerField(max_length=11, blank=True, null = True)
    GCC = models.IntegerField(max_length=11, blank=True, null = True)
    GCA = models.IntegerField(max_length=11, blank=True, null = True)
    GCG = models.IntegerField(max_length=11, blank=True, null = True)
    GGU = models.IntegerField(max_length=11, blank=True, null = True)
    GGC = models.IntegerField(max_length=11, blank=True, null = True)
    GGA = models.IntegerField(max_length=11, blank=True, null = True)
    GGG = models.IntegerField(max_length=11, blank=True, null = True)
    CCU = models.IntegerField(max_length=11, blank=True, null = True)
    CCC = models.IntegerField(max_length=11, blank=True, null = True)
    CCA = models.IntegerField(max_length=11, blank=True, null = True)
    CCG = models.IntegerField(max_length=11, blank=True, null = True)
    ACU = models.IntegerField(max_length=11, blank=True, null = True)
    ACC = models.IntegerField(max_length=11, blank=True, null = True)
    ACA = models.IntegerField(max_length=11, blank=True, null = True)
    ACG = models.IntegerField(max_length=11, blank=True, null = True)
    UCU = models.IntegerField(max_length=11, blank=True, null = True)
    UCC = models.IntegerField(max_length=11, blank=True, null = True)
    UCA = models.IntegerField(max_length=11, blank=True, null = True)
    UCG = models.IntegerField(max_length=11, blank=True, null = True)
    AGU = models.IntegerField(max_length=11, blank=True, null = True)
    AGC = models.IntegerField(max_length=11, blank=True, null = True)
    UAU = models.IntegerField(max_length=11, blank=True, null = True)
    UAC = models.IntegerField(max_length=11, blank=True, null = True)
    UGG = models.IntegerField(max_length=11, blank=True, null = True)
    UUG = models.IntegerField(max_length=11, blank=True, null = True)
    AAU = models.IntegerField(max_length=11, blank=True, null = True)
    AAC = models.IntegerField(max_length=11, blank=True, null = True)
    CAU = models.IntegerField(max_length=11, blank=True, null = True)
    CAC = models.IntegerField(max_length=11, blank=True, null = True)
    GAA = models.IntegerField(max_length=11, blank=True, null = True)
    GAG = models.IntegerField(max_length=11, blank=True, null = True)
    GAU = models.IntegerField(max_length=11, blank=True, null = True)
    GAC = models.IntegerField(max_length=11, blank=True, null = True)
    AAA = models.IntegerField(max_length=11, blank=True, null = True)
    AAG = models.IntegerField(max_length=11, blank=True, null = True)
    CGU = models.IntegerField(max_length=11, blank=True, null = True)
    CGC = models.IntegerField(max_length=11, blank=True, null = True)
    CGA = models.IntegerField(max_length=11, blank=True, null = True)
    CGG = models.IntegerField(max_length=11, blank=True, null = True)
    AGA = models.IntegerField(max_length=11, blank=True, null = True)
    AGG = models.IntegerField(max_length=11, blank=True, null = True)
    UAA = models.IntegerField(max_length=11, blank=True, null = True)
    UAG = models.IntegerField(max_length=11, blank=True, null = True)
    UGA = models.IntegerField(max_length=11, blank=True, null = True)

    def set_codon_usage_from_dictionary(self, codon_usage_dict):
        self.AUU = int(codon_usage_dict['AUU'])
        self.AUC = int(codon_usage_dict['AUC'])
        self.AUA = int(codon_usage_dict['AUA'])
        self.CUU = int(codon_usage_dict['CUU'])
        self.CUC = int(codon_usage_dict['CUC'])
        self.CUA = int(codon_usage_dict['CUA'])
        self.CUG = int(codon_usage_dict['CUG'])
        self.UUA = int(codon_usage_dict['UUA'])
        self.CAA = int(codon_usage_dict['CAA'])
        self.CAG = int(codon_usage_dict['CAG'])
        self.GUU = int(codon_usage_dict['GUU'])
        self.GUC = int(codon_usage_dict['GUC'])
        self.GUA = int(codon_usage_dict['GUA'])
        self.GUG = int(codon_usage_dict['GUG'])
        self.UUU = int(codon_usage_dict['UUU'])
        self.UUC = int(codon_usage_dict['UUC'])
        self.AUG = int(codon_usage_dict['AUG'])
        self.UGU = int(codon_usage_dict['UGU'])
        self.UGC = int(codon_usage_dict['UGC'])
        self.GCU = int(codon_usage_dict['GCU'])
        self.GCC = int(codon_usage_dict['GCC'])
        self.GCA = int(codon_usage_dict['GCA'])
        self.GCG = int(codon_usage_dict['GCG'])
        self.GGU = int(codon_usage_dict['GGU'])
        self.GGC = int(codon_usage_dict['GGC'])
        self.GGA = int(codon_usage_dict['GGA'])
        self.GGG = int(codon_usage_dict['GGG'])
        self.CCU = int(codon_usage_dict['CCU'])
        self.CCC = int(codon_usage_dict['CCC'])
        self.CCA = int(codon_usage_dict['CCA'])
        self.CCG = int(codon_usage_dict['CCG'])
        self.ACU = int(codon_usage_dict['ACU'])
        self.ACC = int(codon_usage_dict['ACC'])
        self.ACA = int(codon_usage_dict['ACA'])
        self.ACG = int(codon_usage_dict['ACG'])
        self.UCU = int(codon_usage_dict['UCU'])
        self.UCC = int(codon_usage_dict['UCC'])
        self.UCA = int(codon_usage_dict['UCA'])
        self.UCG = int(codon_usage_dict['UCG'])
        self.AGU = int(codon_usage_dict['AGU'])
        self.AGC = int(codon_usage_dict['AGC'])
        self.UAU = int(codon_usage_dict['UAU'])
        self.UAC = int(codon_usage_dict['UAC'])
        self.UGG = int(codon_usage_dict['UGG'])
        self.UUG = int(codon_usage_dict['UUG'])
        self.AAU = int(codon_usage_dict['AAU'])
        self.AAC = int(codon_usage_dict['AAC'])
        self.CAU = int(codon_usage_dict['CAU'])
        self.CAC = int(codon_usage_dict['CAC'])
        self.GAA = int(codon_usage_dict['GAA'])
        self.GAG = int(codon_usage_dict['GAG'])
        self.GAU = int(codon_usage_dict['GAU'])
        self.GAC = int(codon_usage_dict['GAC'])
        self.AAA = int(codon_usage_dict['AAA'])
        self.AAG = int(codon_usage_dict['AAG'])
        self.CGU = int(codon_usage_dict['CGU'])
        self.CGC = int(codon_usage_dict['CGC'])
        self.CGA = int(codon_usage_dict['CGA'])
        self.CGG = int(codon_usage_dict['CGG'])
        self.AGA = int(codon_usage_dict['AGA'])
        self.AGG = int(codon_usage_dict['AGG'])
        self.UAA = int(codon_usage_dict['UAA'])
        self.UAG = int(codon_usage_dict['UAG'])
        self.UGA = int(codon_usage_dict['UGA'])

    def to_string(self):
        return "[AUU:%s;AUC:%s;AUA:%s;CUU:%s;CUC:%s ... ]" % (self.AUU, self.AUC, self.AUA, self.CUU, self.CUC)
    
    def get_amino_acids(self):
        return AminoAcid.get_amino_acids()

    def get_aa_frequencies(self):
        return collections.Counter(self.aa)

    def is_empty(self):
        return self.AUU == None and self.AUC == None and  self.AUA == None and  self.CUU == None and self.CUC == None and self.CUA == None and self.CUG == None and self.UUA == None and self.CAA == None and self.CAG == None and self.GUU == None and self.GUC == None and self.GUA == None and self.GUG == None and self.UUU == None and self.UUC == None and self.AUG == None and self.UGU == None and self.UGC == None and self.GCU == None and self.GCC == None and self.GCA == None and self.GCG == None and self.GGU == None and self.GGC == None and self.GGA == None and self.GGG == None and self.CCU == None and self.CCC == None and self.CCA == None and self.CCG == None and self.ACU == None and self.ACC == None and self.ACA == None and self.ACG == None and self.UCU == None and self.UCC == None and self.UCA == None and self.UCG == None and self.AGU == None and self.AGC == None and self.UAU == None and self.UAC == None and self.UGG == None and self.UUG == None and self.AAU == None and self.AAC == None and self.CAU == None and self.CAC == None and self.GAA == None and self.GAG == None and self.GAU == None and self.GAC == None and self.AAA == None and self.AAG == None and self.CGU == None and self.CGC == None and self.CGA == None and self.CGG == None and self.AGA == None and self.AGG == None and self.UAA == None and self.UAG == None and self.UGA == None and self.aa==None and self.size==None

    def same_values(self, other):
        return self.AUU == other.AUU and self.AUC == other.AUC and  self.AUA == other.AUA and  self.CUU == other.CUU and self.CUC == other.CUC and self.CUA == other.CUA and self.CUG == other.CUG and self.UUA == other.UUA and self.CAA == other.CAA and self.CAG == other.CAG and self.GUU == other.GUU and self.GUC == other.GUC and self.GUA == other.GUA and self.GUG == other.GUG and self.UUU == other.UUU and self.UUC == other.UUC and self.AUG == other.AUG and self.UGU == other.UGU and self.UGC == other.UGC and self.GCU == other.GCU and self.GCC == other.GCC and self.GCA == other.GCA and self.GCG == other.GCG and self.GGU == other.GGU and self.GGC == other.GGC and self.GGA == other.GGA and self.GGG == other.GGG and self.CCU == other.CCU and self.CCC == other.CCC and self.CCA == other.CCA and self.CCG == other.CCG and self.ACU == other.ACU and self.ACC == other.ACC and self.ACA == other.ACA and self.ACG == other.ACG and self.UCU == other.UCU and self.UCC == other.UCC and self.UCA == other.UCA and self.UCG == other.UCG and self.AGU == other.AGU and self.AGC == other.AGC and self.UAU == other.UAU and self.UAC == other.UAC and self.UGG == other.UGG and self.UUG == other.UUG and self.AAU == other.AAU and self.AAC == other.AAC and self.CAU == other.CAU and self.CAC == other.CAC and self.GAA == other.GAA and self.GAG == other.GAG and self.GAU == other.GAU and self.GAC == other.GAC and self.AAA == other.AAA and self.AAG == other.AAG and self.CGU == other.CGU and self.CGC == other.CGC and self.CGA == other.CGA and self.CGG == other.CGG and self.AGA == other.AGA and self.AGG == other.AGG and self.UAA == other.UAA and self.UAG == other.UAG and self.UGA == other.UGA and self.aa==other.aa and self.size==other.size

    def codons_1st_g(self):
        return self.GAA + self.GAC + self.GAG + self.GAU + self.GCA + self.GCC + self.GCG + self.GCU + self.GGA + self.GGC + self.GGG + self.GGU + self.GUA + self.GUC + self.GUG + self.GUU

    def codons_1st_c(self):
        return self.CAA + self.CAC + self.CAG + self.CAU + self.CCA + self.CCC + self.CCG + self.CCU + self.CGA + self.CGC + self.CGG + self.CGU + self.CUA + self.CUC + self.CUG + self.CUU

    def codons_1st_a(self):
        return self.AAA + self.AAC + self.AAG + self.AAU + self.ACA + self.ACC + self.ACG + self.ACU + self.AGA + self.AGC + self.AGG + self.AGU + self.AUA + self.AUC + self.AUG + self.AUU

    def codons_1st_u(self):
        return self.UAC + self.UAU + self.UAA + self.UAG + self.UCA + self.UCC + self.UCG + self.UCU + self.UGC + self.UGG + self.UGU + self.UGA + self.UUA + self.UUC + self.UUG + self.UUU


    def codons_2nd_g(self):
        return self.AGA + self.AGC + self.AGG + self.AGU + self.CGA + self.CGC + self.CGG + self.CGU + self.GGA + self.GGC + self.GGG + self.GGU + self.UGA + self.UGC + self.UGG + self.UGU

    def codons_2nd_c(self):
        return self.ACA + self.ACC + self.ACG + self.ACU + self.CCA + self.CCC + self.CCG + self.CCU + self.GCA + self.GCC + self.GCG + self.GCU + self.UCA + self.UCC + self.UCG + self.UCU

    def codons_2nd_a(self):
        return self.AAA + self.AAC + self.AAG + self.AAU + self.CAA + self.CAC + self.CAG + self.CAU + self.GAA + self.GAC + self.GAG + self.GAU + self.UAA + self.UAC + self.UAG + self.UAU

    def codons_2nd_u(self):
        return self.AUC + self.AUU + self.CUA + self.CUC + self.CUG + self.CUU + self.GUC + self.GUG + self.GUU + self.AUA + self.AUG + self.GUA  + self.UUA + self.UUC + self.UUG + self.UUU


    def codons_3rd_g(self):
        return self.AAG + self.ACG + self.AGG + self.AUG + self.CAG + self.CCG + self.CGG + self.CUG + self.GAG + self.GCG + self.GGG + self.GUG + self.UAG + self.UCG + self.UGG + self.UUG

    def codons_3rd_c(self):
        return self.AAC + self.ACC + self.AGC + self.AUC + self.CAC + self.CCC + self.CGC + self.CUC + self.GAC + self.GCC + self.GGC + self.GUC + self.UAC + self.UCC + self.UGC + self.UUC

    def codons_3rd_a(self):
        return self.AAA + self.ACA + self.AGA + self.AUA + self.CAA + self.CCA + self.CGA + self.CUA + self.GAA + self.GCA + self.GGA + self.GUA + self.UAA + self.UCA + self.UGA + self.UUA

    def codons_3rd_u(self):
        return self.ACU + self.AUU + self.CAU + self.CCU + self.CGU + self.CUU + self.GCU + self.GGU + self.GUU + self.AAU + self.AGU + self.GAU  + self.UAU + self.UCU + self.UGU + self.UUU


class MitoAgeEntry(models.Model):
    class Meta:
        verbose_name = "MitoAge entry"
        verbose_name_plural = "MitoAge entries"
    
    species = models.ForeignKey(TaxonomySpecies, related_name='mitoage_entries')

    #Sections with base composition
    #    Total mtDNA
    bc_total_mtDNA_size = models.IntegerField("Size of total mtDNA", max_length=11, blank=True, null = True)
    bc_total_mtDNA_g = models.IntegerField("G content", max_length=11, blank=True, null = True)
    bc_total_mtDNA_c = models.IntegerField("C content", max_length=11, blank=True, null = True)
    bc_total_mtDNA_t = models.IntegerField("T content", max_length=11, blank=True, null = True)
    bc_total_mtDNA_a = models.IntegerField("A content", max_length=11, blank=True, null = True)
    bc_total_mtDNA_others = models.IntegerField("Other", max_length=11, blank=True, null = True)

    #    Total protein coding DNA
    bc_total_mtDNA_pc_size = models.IntegerField("Size of protein-coding region of mtDNA", max_length=11, blank=True, null = True)
    bc_total_mtDNA_pc_g = models.IntegerField("G content", max_length=11, blank=True, null = True)
    bc_total_mtDNA_pc_c = models.IntegerField("C content", max_length=11, blank=True, null = True)
    bc_total_mtDNA_pc_t = models.IntegerField("T content", max_length=11, blank=True, null = True)
    bc_total_mtDNA_pc_a = models.IntegerField("A content", max_length=11, blank=True, null = True)
    bc_total_mtDNA_bc_others = models.IntegerField("Other", max_length=11, blank=True, null = True)
    
    #    Total d-loop region
    bc_d_loop_size = models.IntegerField("Size of D-loop region", max_length=11, blank=True, null = True)
    bc_d_loop_g = models.IntegerField("G content", max_length=11, blank=True, null = True)
    bc_d_loop_c = models.IntegerField("C content", max_length=11, blank=True, null = True)
    bc_d_loop_t = models.IntegerField("T content", max_length=11, blank=True, null = True)
    bc_d_loop_a = models.IntegerField("A content", max_length=11, blank=True, null = True)
    bc_d_loop_others = models.IntegerField("Other", max_length=11, blank=True, null = True)

    #    Total tRNA region
    bc_total_tRNA_size = models.IntegerField("Size of tRNA region of mtDNA", max_length=11, blank=True, null = True)
    bc_total_tRNA_g = models.IntegerField("G content", max_length=11, blank=True, null = True)
    bc_total_tRNA_c = models.IntegerField("C content", max_length=11, blank=True, null = True)
    bc_total_tRNA_t = models.IntegerField("T content", max_length=11, blank=True, null = True)
    bc_total_tRNA_a = models.IntegerField("A content", max_length=11, blank=True, null = True)
    bc_total_tRNA_others = models.IntegerField("Other", max_length=11, blank=True, null = True)

    #    Total rRNA region
    bc_total_rRNA_size = models.IntegerField("Size of rRNA region of mtDNA", max_length=11, blank=True, null = True)
    bc_total_rRNA_g = models.IntegerField("G content", max_length=11, blank=True, null = True)
    bc_total_rRNA_c = models.IntegerField("C content", max_length=11, blank=True, null = True)
    bc_total_rRNA_t = models.IntegerField("T content", max_length=11, blank=True, null = True)
    bc_total_rRNA_a = models.IntegerField("A content", max_length=11, blank=True, null = True)
    bc_total_rRNA_others = models.IntegerField("Other", max_length=11, blank=True, null = True)

    #Individual genes (13pc + 2rRNA tables)
    #    atp6
    bc_atp6_size = models.IntegerField("Size of gene", max_length=11, blank=True, null = True)
    bc_atp6_g = models.IntegerField("G content", max_length=11, blank=True, null = True)
    bc_atp6_c = models.IntegerField("C content", max_length=11, blank=True, null = True)
    bc_atp6_t = models.IntegerField("T content", max_length=11, blank=True, null = True)
    bc_atp6_a = models.IntegerField("A content", max_length=11, blank=True, null = True)
    bc_atp6_others = models.IntegerField("Other", max_length=11, blank=True, null = True)

    #    atp8
    bc_atp8_size = models.IntegerField("Size of gene", max_length=11, blank=True, null = True)
    bc_atp8_g = models.IntegerField("G content", max_length=11, blank=True, null = True)
    bc_atp8_c = models.IntegerField("C content", max_length=11, blank=True, null = True)
    bc_atp8_t = models.IntegerField("T content", max_length=11, blank=True, null = True)
    bc_atp8_a = models.IntegerField("A content", max_length=11, blank=True, null = True)
    bc_atp8_others = models.IntegerField("Other", max_length=11, blank=True, null = True)

    #    cox1
    bc_cox1_size = models.IntegerField("Size of gene", max_length=11, blank=True, null = True)
    bc_cox1_g = models.IntegerField("G content", max_length=11, blank=True, null = True)
    bc_cox1_c = models.IntegerField("C content", max_length=11, blank=True, null = True)
    bc_cox1_t = models.IntegerField("T content", max_length=11, blank=True, null = True)
    bc_cox1_a = models.IntegerField("A content", max_length=11, blank=True, null = True)
    bc_cox1_others = models.IntegerField("Other", max_length=11, blank=True, null = True)

    #    cox2
    bc_cox2_size = models.IntegerField("Size of gene", max_length=11, blank=True, null = True)
    bc_cox2_g = models.IntegerField("G content", max_length=11, blank=True, null = True)
    bc_cox2_c = models.IntegerField("C content", max_length=11, blank=True, null = True)
    bc_cox2_t = models.IntegerField("T content", max_length=11, blank=True, null = True)
    bc_cox2_a = models.IntegerField("A content", max_length=11, blank=True, null = True)
    bc_cox2_others = models.IntegerField("Other", max_length=11, blank=True, null = True)

    #    cox3
    bc_cox3_size = models.IntegerField("Size of gene", max_length=11, blank=True, null = True)
    bc_cox3_g = models.IntegerField("G content", max_length=11, blank=True, null = True)
    bc_cox3_c = models.IntegerField("C content", max_length=11, blank=True, null = True)
    bc_cox3_t = models.IntegerField("T content", max_length=11, blank=True, null = True)
    bc_cox3_a = models.IntegerField("A content", max_length=11, blank=True, null = True)
    bc_cox3_others = models.IntegerField("Other", max_length=11, blank=True, null = True)

    #    cytb
    bc_cytb_size = models.IntegerField("Size of gene", max_length=11, blank=True, null = True)
    bc_cytb_g = models.IntegerField("G content", max_length=11, blank=True, null = True)
    bc_cytb_c = models.IntegerField("C content", max_length=11, blank=True, null = True)
    bc_cytb_t = models.IntegerField("T content", max_length=11, blank=True, null = True)
    bc_cytb_a = models.IntegerField("A content", max_length=11, blank=True, null = True)
    bc_cytb_others = models.IntegerField("Other", max_length=11, blank=True, null = True)

    #    nd1
    bc_nd1_size = models.IntegerField("Size of gene", max_length=11, blank=True, null = True)
    bc_nd1_g = models.IntegerField("G content", max_length=11, blank=True, null = True)
    bc_nd1_c = models.IntegerField("C content", max_length=11, blank=True, null = True)
    bc_nd1_t = models.IntegerField("T content", max_length=11, blank=True, null = True)
    bc_nd1_a = models.IntegerField("A content", max_length=11, blank=True, null = True)
    bc_nd1_others = models.IntegerField("Other", max_length=11, blank=True, null = True)

    #    nd2
    bc_nd2_size = models.IntegerField("Size of gene", max_length=11, blank=True, null = True)
    bc_nd2_g = models.IntegerField("G content", max_length=11, blank=True, null = True)
    bc_nd2_c = models.IntegerField("C content", max_length=11, blank=True, null = True)
    bc_nd2_t = models.IntegerField("T content", max_length=11, blank=True, null = True)
    bc_nd2_a = models.IntegerField("A content", max_length=11, blank=True, null = True)
    bc_nd2_others = models.IntegerField("Other", max_length=11, blank=True, null = True)

    #    nd3
    bc_nd3_size = models.IntegerField("Size of gene", max_length=11, blank=True, null = True)
    bc_nd3_g = models.IntegerField("G content", max_length=11, blank=True, null = True)
    bc_nd3_c = models.IntegerField("C content", max_length=11, blank=True, null = True)
    bc_nd3_t = models.IntegerField("T content", max_length=11, blank=True, null = True)
    bc_nd3_a = models.IntegerField("A content", max_length=11, blank=True, null = True)
    bc_nd3_others = models.IntegerField("Other", max_length=11, blank=True, null = True)

    #    nd4
    bc_nd4_size = models.IntegerField("Size of gene", max_length=11, blank=True, null = True)
    bc_nd4_g = models.IntegerField("G content", max_length=11, blank=True, null = True)
    bc_nd4_c = models.IntegerField("C content", max_length=11, blank=True, null = True)
    bc_nd4_t = models.IntegerField("T content", max_length=11, blank=True, null = True)
    bc_nd4_a = models.IntegerField("A content", max_length=11, blank=True, null = True)
    bc_nd4_others = models.IntegerField("Other", max_length=11, blank=True, null = True)

    #    nd4l
    bc_nd4l_size = models.IntegerField("Size of gene", max_length=11, blank=True, null = True)
    bc_nd4l_g = models.IntegerField("G content", max_length=11, blank=True, null = True)
    bc_nd4l_c = models.IntegerField("C content", max_length=11, blank=True, null = True)
    bc_nd4l_t = models.IntegerField("T content", max_length=11, blank=True, null = True)
    bc_nd4l_a = models.IntegerField("A content", max_length=11, blank=True, null = True)
    bc_nd4l_others = models.IntegerField("Other", max_length=11, blank=True, null = True)

    #    nd5
    bc_nd5_size = models.IntegerField("Size of gene", max_length=11, blank=True, null = True)
    bc_nd5_g = models.IntegerField("G content", max_length=11, blank=True, null = True)
    bc_nd5_c = models.IntegerField("C content", max_length=11, blank=True, null = True)
    bc_nd5_t = models.IntegerField("T content", max_length=11, blank=True, null = True)
    bc_nd5_a = models.IntegerField("A content", max_length=11, blank=True, null = True)
    bc_nd5_others = models.IntegerField("Other", max_length=11, blank=True, null = True)

    #    nd6
    bc_nd6_size = models.IntegerField("Size of gene", max_length=11, blank=True, null = True)
    bc_nd6_g = models.IntegerField("G content", max_length=11, blank=True, null = True)
    bc_nd6_c = models.IntegerField("C content", max_length=11, blank=True, null = True)
    bc_nd6_t = models.IntegerField("T content", max_length=11, blank=True, null = True)
    bc_nd6_a = models.IntegerField("A content", max_length=11, blank=True, null = True)
    bc_nd6_others = models.IntegerField("Other", max_length=11, blank=True, null = True)

    #    rRNA 12S
    bc_rRNA_12S_size = models.IntegerField("Size of ribosomal subunit", max_length=11, blank=True, null = True)
    bc_rRNA_12S_g = models.IntegerField("G content", max_length=11, blank=True, null = True)
    bc_rRNA_12S_c = models.IntegerField("C content", max_length=11, blank=True, null = True)
    bc_rRNA_12S_t = models.IntegerField("T content", max_length=11, blank=True, null = True)
    bc_rRNA_12S_a = models.IntegerField("A content", max_length=11, blank=True, null = True)
    bc_rRNA_12S_others = models.IntegerField("Other", max_length=11, blank=True, null = True)

    #    rRNA 12S
    bc_rRNA_16S_size = models.IntegerField("Size of ribosomal subunit", max_length=11, blank=True, null = True)
    bc_rRNA_16S_g = models.IntegerField("G content", max_length=11, blank=True, null = True)
    bc_rRNA_16S_c = models.IntegerField("C content", max_length=11, blank=True, null = True)
    bc_rRNA_16S_t = models.IntegerField("T content", max_length=11, blank=True, null = True)
    bc_rRNA_16S_a = models.IntegerField("A content", max_length=11, blank=True, null = True)
    bc_rRNA_16S_others = models.IntegerField("Other", max_length=11, blank=True, null = True)

    def __unicode__(self):
        return u"mtDNA analysis of %s " % self.species.name

    def get_base_compositions_as_dictionaries(self):
        return {key: self.get_base_composition(key) for key in BaseComposition.get_bc_sections()}

    def get_codon_usages_as_dictionaries(self):
        return {key: self.get_codon_usage(key) for key in CodonUsage.get_cu_sections()}

    def get_base_composition(self, type_of_bc):
        return {
            'total_mtDNA': BaseComposition(self.bc_total_mtDNA_size, self.bc_total_mtDNA_g, self.bc_total_mtDNA_c, self.bc_total_mtDNA_a, self.bc_total_mtDNA_t, self.bc_total_mtDNA_others),
            'total_pc_mtDNA': BaseComposition(self.bc_total_mtDNA_pc_size, self.bc_total_mtDNA_pc_g, self.bc_total_mtDNA_pc_c, self.bc_total_mtDNA_pc_a, self.bc_total_mtDNA_pc_t, self.bc_total_mtDNA_bc_others),
            'd_loop_mtDNA': BaseComposition(self.bc_d_loop_size, self.bc_d_loop_g, self.bc_d_loop_c, self.bc_d_loop_a, self.bc_d_loop_t, self.bc_d_loop_others),
            'total_tRNA_mtDNA': BaseComposition(self.bc_total_tRNA_size, self.bc_total_tRNA_g, self.bc_total_tRNA_c, self.bc_total_tRNA_a, self.bc_total_tRNA_t, self.bc_total_tRNA_others),
            'total_rRNA_mtDNA': BaseComposition(self.bc_total_rRNA_size, self.bc_total_rRNA_g, self.bc_total_rRNA_c, self.bc_total_rRNA_a, self.bc_total_rRNA_t, self.bc_total_rRNA_others),
            'atp6': BaseComposition(self.bc_atp6_size, self.bc_atp6_g, self.bc_atp6_c, self.bc_atp6_a, self.bc_atp6_t, self.bc_atp6_others),
            'atp8': BaseComposition(self.bc_atp8_size, self.bc_atp8_g, self.bc_atp8_c, self.bc_atp8_a, self.bc_atp8_t, self.bc_atp8_others),
            'cox1': BaseComposition(self.bc_cox1_size, self.bc_cox1_g, self.bc_cox1_c, self.bc_cox1_a, self.bc_cox1_t, self.bc_cox1_others),
            'cox2': BaseComposition(self.bc_cox2_size, self.bc_cox2_g, self.bc_cox2_c, self.bc_cox2_a, self.bc_cox2_t, self.bc_cox2_others),
            'cox3': BaseComposition(self.bc_cox3_size, self.bc_cox3_g, self.bc_cox3_c, self.bc_cox3_a, self.bc_cox3_t, self.bc_cox3_others),
            'cytb': BaseComposition(self.bc_cytb_size, self.bc_cytb_g, self.bc_cytb_c, self.bc_cytb_a, self.bc_cytb_t, self.bc_cytb_others),
            'nd1': BaseComposition(self.bc_nd1_size, self.bc_nd1_g, self.bc_nd1_c, self.bc_nd1_a, self.bc_nd1_t, self.bc_nd1_others),
            'nd2': BaseComposition(self.bc_nd2_size, self.bc_nd2_g, self.bc_nd2_c, self.bc_nd2_a, self.bc_nd2_t, self.bc_nd2_others),
            'nd3': BaseComposition(self.bc_nd3_size, self.bc_nd3_g, self.bc_nd3_c, self.bc_nd3_a, self.bc_nd3_t, self.bc_nd3_others),
            'nd4': BaseComposition(self.bc_nd4_size, self.bc_nd4_g, self.bc_nd4_c, self.bc_nd4_a, self.bc_nd4_t, self.bc_nd4_others),
            'nd4l': BaseComposition(self.bc_nd4l_size, self.bc_nd4l_g, self.bc_nd4l_c, self.bc_nd4l_a, self.bc_nd4l_t, self.bc_nd4l_others),
            'nd5': BaseComposition(self.bc_nd5_size, self.bc_nd5_g, self.bc_nd5_c, self.bc_nd5_a, self.bc_nd5_t, self.bc_nd5_others),
            'nd6': BaseComposition(self.bc_nd6_size, self.bc_nd6_g, self.bc_nd6_c, self.bc_nd6_a, self.bc_nd6_t, self.bc_nd6_others),
            'rRNA_12S': BaseComposition(self.bc_rRNA_12S_size, self.bc_rRNA_12S_g, self.bc_rRNA_12S_c, self.bc_rRNA_12S_a, self.bc_rRNA_12S_t, self.bc_rRNA_12S_others),
            'rRNA_16S': BaseComposition(self.bc_rRNA_16S_size, self.bc_rRNA_16S_g, self.bc_rRNA_16S_c, self.bc_rRNA_16S_a, self.bc_rRNA_16S_t, self.bc_rRNA_16S_others),
        }[type_of_bc]
    
    def set_base_composition(self, type_of_bc, base_composition):
        if type_of_bc=='total_mtDNA':
            (self.bc_total_mtDNA_size, self.bc_total_mtDNA_g, self.bc_total_mtDNA_c, self.bc_total_mtDNA_a, self.bc_total_mtDNA_t, self.bc_total_mtDNA_others) = base_composition.to_raw_data()
        if type_of_bc=='total_pc_mtDNA':
            (self.bc_total_mtDNA_pc_size, self.bc_total_mtDNA_pc_g, self.bc_total_mtDNA_pc_c, self.bc_total_mtDNA_pc_a, self.bc_total_mtDNA_pc_t, self.bc_total_mtDNA_bc_others) = base_composition.to_raw_data()
        if type_of_bc=='d_loop_mtDNA':
            (self.bc_d_loop_size, self.bc_d_loop_g, self.bc_d_loop_c, self.bc_d_loop_a, self.bc_d_loop_t, self.bc_d_loop_others) = base_composition.to_raw_data()
        if type_of_bc=='total_tRNA_mtDNA':
            (self.bc_total_tRNA_size, self.bc_total_tRNA_g, self.bc_total_tRNA_c, self.bc_total_tRNA_a, self.bc_total_tRNA_t, self.bc_total_tRNA_others) = base_composition.to_raw_data()
        if type_of_bc=='total_rRNA_mtDNA':
            (self.bc_total_rRNA_size, self.bc_total_rRNA_g, self.bc_total_rRNA_c, self.bc_total_rRNA_a, self.bc_total_rRNA_t, self.bc_total_rRNA_others) = base_composition.to_raw_data()
        if type_of_bc=='atp6':
            (self.bc_atp6_size, self.bc_atp6_g, self.bc_atp6_c, self.bc_atp6_a, self.bc_atp6_t, self.bc_atp6_others) = base_composition.to_raw_data()
        if type_of_bc=='atp8':
            (self.bc_atp8_size, self.bc_atp8_g, self.bc_atp8_c, self.bc_atp8_a, self.bc_atp8_t, self.bc_atp8_others) = base_composition.to_raw_data()
        if type_of_bc=='cox1':
            (self.bc_cox1_size, self.bc_cox1_g, self.bc_cox1_c, self.bc_cox1_a, self.bc_cox1_t, self.bc_cox1_others) = base_composition.to_raw_data()
        if type_of_bc=='cox2':
            (self.bc_cox2_size, self.bc_cox2_g, self.bc_cox2_c, self.bc_cox2_a, self.bc_cox2_t, self.bc_cox2_others) = base_composition.to_raw_data()
        if type_of_bc=='cox3':
            (self.bc_cox3_size, self.bc_cox3_g, self.bc_cox3_c, self.bc_cox3_a, self.bc_cox3_t, self.bc_cox3_others) = base_composition.to_raw_data()
        if type_of_bc=='cytb':
            (self.bc_cytb_size, self.bc_cytb_g, self.bc_cytb_c, self.bc_cytb_a, self.bc_cytb_t, self.bc_cytb_others) = base_composition.to_raw_data()
        if type_of_bc=='nd1':
            (self.bc_nd1_size, self.bc_nd1_g, self.bc_nd1_c, self.bc_nd1_a, self.bc_nd1_t, self.bc_nd1_others) = base_composition.to_raw_data()
        if type_of_bc=='nd2':
            (self.bc_nd2_size, self.bc_nd2_g, self.bc_nd2_c, self.bc_nd2_a, self.bc_nd2_t, self.bc_nd2_others) = base_composition.to_raw_data()
        if type_of_bc=='nd3':
            (self.bc_nd3_size, self.bc_nd3_g, self.bc_nd3_c, self.bc_nd3_a, self.bc_nd3_t, self.bc_nd3_others) = base_composition.to_raw_data()
        if type_of_bc=='nd4':
            (self.bc_nd4_size, self.bc_nd4_g, self.bc_nd4_c, self.bc_nd4_a, self.bc_nd4_t, self.bc_nd4_others) = base_composition.to_raw_data()
        if type_of_bc=='nd4l':
            (self.bc_nd4l_size, self.bc_nd4l_g, self.bc_nd4l_c, self.bc_nd4l_a, self.bc_nd4l_t, self.bc_nd4l_others) = base_composition.to_raw_data()
        if type_of_bc=='nd5':
            (self.bc_nd5_size, self.bc_nd5_g, self.bc_nd5_c, self.bc_nd5_a, self.bc_nd5_t, self.bc_nd5_others) = base_composition.to_raw_data()
        if type_of_bc=='nd6':
            (self.bc_nd6_size, self.bc_nd6_g, self.bc_nd6_c, self.bc_nd6_a, self.bc_nd6_t, self.bc_nd6_others) = base_composition.to_raw_data()
        if type_of_bc=='rRNA_12S':
            (self.bc_rRNA_12S_size, self.bc_rRNA_12S_g, self.bc_rRNA_12S_c, self.bc_rRNA_12S_a, self.bc_rRNA_12S_t, self.bc_rRNA_12S_others) = base_composition.to_raw_data()
        if type_of_bc=='rRNA_16S':
            (self.bc_rRNA_16S_size, self.bc_rRNA_16S_g, self.bc_rRNA_16S_c, self.bc_rRNA_16S_a, self.bc_rRNA_16S_t, self.bc_rRNA_16S_others) = base_composition.to_raw_data()
        
    
    def get_codon_usage(self, type_of_cu):
        try:
            if type_of_cu=='total_pc_mtDNA':
                return self.protein_coding_codon_usage
            if type_of_cu=='atp6':
                return self.atp6_codon_usage
            if type_of_cu=='atp8':
                return self.atp8_codon_usage
            if type_of_cu=='cox1':
                return self.cox1_codon_usage
            if type_of_cu=='cox2':
                return self.cox2_codon_usage
            if type_of_cu=='cox3':
                return self.cox3_codon_usage
            if type_of_cu=='cytb':
                return self.cytb_codon_usage
            if type_of_cu=='nd1':
                return self.nd1_codon_usage
            if type_of_cu=='nd2':
                return self.nd2_codon_usage
            if type_of_cu=='nd3':
                return self.nd3_codon_usage
            if type_of_cu=='nd4':
                return self.nd4_codon_usage
            if type_of_cu=='nd4l':
                return self.nd4l_codon_usage
            if type_of_cu=='nd5':
                return self.nd5_codon_usage
            if type_of_cu=='nd6':
                return self.nd6_codon_usage
        except CodonUsage.DoesNotExist:
            return None
        return None
    
    def set_codon_usage(self, type_of_cu, codon_usage):
        if type_of_cu=='total_pc_mtDNA':
            #self.protein_coding_codon_usage = codon_usage
            codon_usage.cu_protein_coding_entry = self
        if type_of_cu=='atp6':
            codon_usage.cu_atp6_entry = self
            #self.atp6_codon_usage = codon_usage
        if type_of_cu=='atp8':
            codon_usage.cu_atp8_entry = self
            #self.atp8_codon_usage = codon_usage
        if type_of_cu=='cox1':
            codon_usage.cu_cox1_entry = self
            #self.cox1_codon_usage = codon_usage
        if type_of_cu=='cox2':
            codon_usage.cu_cox2_entry = self
            #self.cox2_codon_usage = codon_usage
        if type_of_cu=='cox3':
            codon_usage.cu_cox3_entry = self
            #self.cox3_codon_usage = codon_usage
        if type_of_cu=='cytb':
            codon_usage.cu_cytb_entry = self
            #self.cytb_codon_usage = codon_usage
        if type_of_cu=='nd1':
            codon_usage.cu_nd1_entry = self
            #self.nd1_codon_usage = codon_usage
        if type_of_cu=='nd2':
            codon_usage.cu_nd2_entry = self
            #self.nd2_codon_usage = codon_usage
        if type_of_cu=='nd3':
            codon_usage.cu_nd3_entry = self
            #self.nd3_codon_usage = codon_usage
        if type_of_cu=='nd4':
            codon_usage.cu_nd4_entry = self
            #self.nd4_codon_usage = codon_usage
        if type_of_cu=='nd4l':
            codon_usage.cu_nd4l_entry = self
            #self.nd4l_codon_usage = codon_usage
        if type_of_cu=='nd5':
            codon_usage.cu_nd5_entry = self
            #self.nd5_codon_usage = codon_usage
        if type_of_cu=='nd6':
            codon_usage.cu_nd6_entry = self
            #self.nd6_codon_usage = codon_usage
