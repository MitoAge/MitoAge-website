from django.db import models

from mitoage.taxonomy.models import TaxonomySpecies


class BaseComposition():
    def __init__(self, size, g, c, a, t, others):
        self.size = size
        self.g = g
        self.c = c
        self.a = a
        self.t = t
        self.others = others

    def is_same(self, other):
        return self.size==other.size and self.g==other.g and self.c==other.c and self.a==other.a and self.t==other.t and self.others==other.others 

    def is_empty(self):
        return self.size==None and self.g==None and self.c==None and self.a==None and self.t==None and self.others==None 

    def to_raw_data(self):
        return (self.size, self.g, self.c, self.a, self.t, self.others)
    
    def to_string(self):
        return "[G:%s;C:%s;A:%s;T:%s;O:%s] - size: %s bp" % (self.g, self.c, self.a, self.t, self.others, self.size)

class CodonUsage(models.Model):
    
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
    STOP_UAA = models.IntegerField(max_length=11, blank=True, null = True)
    STOP_UAG = models.IntegerField(max_length=11, blank=True, null = True)
    STOP_UGA = models.IntegerField(max_length=11, blank=True, null = True)

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
        self.STOP_UAA = int(codon_usage_dict['STOP CODON - UAA'])
        self.STOP_UAG = int(codon_usage_dict['STOP CODON - UAG'])
        self.STOP_UGA = int(codon_usage_dict['STOP CODON - UGA'])

    def to_string(self):
        return "[AUU:%s;AUC:%s;AUA:%s;CUU:%s;CUC:%s ... ]" % (self.AUU, self.AUC, self.AUA, self.CUU, self.CUC)

    def same_values(self, other):
        return self.AUU == other.AUU and self.AUC == other.AUC and  self.AUA == other.AUA and  self.CUU == other.CUU and self.CUC == other.CUC and self.CUA == other.CUA and self.CUG == other.CUG and self.UUA == other.UUA and self.CAA == other.CAA and self.CAG == other.CAG and self.GUU == other.GUU and self.GUC == other.GUC and self.GUA == other.GUA and self.GUG == other.GUG and self.UUU == other.UUU and self.UUC == other.UUC and self.AUG == other.AUG and self.UGU == other.UGU and self.UGC == other.UGC and self.GCU == other.GCU and self.GCC == other.GCC and self.GCA == other.GCA and self.GCG == other.GCG and self.GGU == other.GGU and self.GGC == other.GGC and self.GGA == other.GGA and self.GGG == other.GGG and self.CCU == other.CCU and self.CCC == other.CCC and self.CCA == other.CCA and self.CCG == other.CCG and self.ACU == other.ACU and self.ACC == other.ACC and self.ACA == other.ACA and self.ACG == other.ACG and self.UCU == other.UCU and self.UCC == other.UCC and self.UCA == other.UCA and self.UCG == other.UCG and self.AGU == other.AGU and self.AGC == other.AGC and self.UAU == other.UAU and self.UAC == other.UAC and self.UGG == other.UGG and self.UUG == other.UUG and self.AAU == other.AAU and self.AAC == other.AAC and self.CAU == other.CAU and self.CAC == other.CAC and self.GAA == other.GAA and self.GAG == other.GAG and self.GAU == other.GAU and self.GAC == other.GAC and self.AAA == other.AAA and self.AAG == other.AAG and self.CGU == other.CGU and self.CGC == other.CGC and self.CGA == other.CGA and self.CGG == other.CGG and self.AGA == other.AGA and self.AGG == other.AGG and self.STOP_UAA == other.STOP_UAA and self.STOP_UAG == other.STOP_UAG and self.STOP_UGA == other.STOP_UGA and self.aa==other.aa and self.size==other.size

class MitoAgeEntry(models.Model):
    class Meta:
        verbose_name = "MitoAge entry"
        verbose_name_plural = "MitoAge entries"
    
    species = models.ForeignKey(TaxonomySpecies, related_name='species')

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

    @staticmethod
    def get_bc_sections():
        return ['total_mtDNA', 'total_pc_mtDNA', 'd_loop_mtDNA', 'total_rRNA_mtDNA', 'atp6', 'atp8', 'cox1', 'cox2', 'cox3', 'cytb', 'nd1', 'nd2', 'nd3', 'nd4', 'nd4l', 'nd5', 'nd6', 'rRNA_12S', 'rRNA_16S']

    @staticmethod
    def get_cu_sections():
        return ['total_pc_mtDNA', 'atp6', 'atp8', 'cox1', 'cox2', 'cox3', 'cytb', 'nd1', 'nd2', 'nd3', 'nd4', 'nd4l', 'nd5', 'nd6']

    def get_base_composition(self, type_of_bc):
        return {
            'total_mtDNA': BaseComposition(self.bc_total_mtDNA_size, self.bc_total_mtDNA_g, self.bc_total_mtDNA_c, self.bc_total_mtDNA_t, self.bc_total_mtDNA_a, self.bc_total_mtDNA_others),
            'total_pc_mtDNA': BaseComposition(self.bc_total_mtDNA_pc_size, self.bc_total_mtDNA_pc_g, self.bc_total_mtDNA_pc_c, self.bc_total_mtDNA_pc_t, self.bc_total_mtDNA_pc_a, self.bc_total_mtDNA_bc_others),
            'd_loop_mtDNA': BaseComposition(self.bc_d_loop_size, self.bc_d_loop_g, self.bc_d_loop_c, self.bc_d_loop_t, self.bc_d_loop_a, self.bc_d_loop_others),
            'total_rRNA_mtDNA': BaseComposition(self.bc_total_rRNA_size, self.bc_total_rRNA_g, self.bc_total_rRNA_c, self.bc_total_rRNA_t, self.bc_total_rRNA_a, self.bc_total_rRNA_others),
            'atp6': BaseComposition(self.bc_atp6_size, self.bc_atp6_g, self.bc_atp6_c, self.bc_atp6_t, self.bc_atp6_a, self.bc_atp6_others),
            'atp8': BaseComposition(self.bc_atp8_size, self.bc_atp8_g, self.bc_atp8_c, self.bc_atp8_t, self.bc_atp8_a, self.bc_atp8_others),
            'cox1': BaseComposition(self.bc_cox1_size, self.bc_cox1_g, self.bc_cox1_c, self.bc_cox1_t, self.bc_cox1_a, self.bc_cox1_others),
            'cox2': BaseComposition(self.bc_cox2_size, self.bc_cox2_g, self.bc_cox2_c, self.bc_cox2_t, self.bc_cox2_a, self.bc_cox2_others),
            'cox3': BaseComposition(self.bc_cox3_size, self.bc_cox3_g, self.bc_cox3_c, self.bc_cox3_t, self.bc_cox3_a, self.bc_cox3_others),
            'cytb': BaseComposition(self.bc_cytb_size, self.bc_cytb_g, self.bc_cytb_c, self.bc_cytb_t, self.bc_cytb_a, self.bc_cytb_others),
            'nd1': BaseComposition(self.bc_nd1_size, self.bc_nd1_g, self.bc_nd1_c, self.bc_nd1_t, self.bc_nd1_a, self.bc_nd1_others),
            'nd2': BaseComposition(self.bc_nd2_size, self.bc_nd2_g, self.bc_nd2_c, self.bc_nd2_t, self.bc_nd2_a, self.bc_nd2_others),
            'nd3': BaseComposition(self.bc_nd3_size, self.bc_nd3_g, self.bc_nd3_c, self.bc_nd3_t, self.bc_nd3_a, self.bc_nd3_others),
            'nd4': BaseComposition(self.bc_nd4_size, self.bc_nd4_g, self.bc_nd4_c, self.bc_nd4_t, self.bc_nd4_a, self.bc_nd4_others),
            'nd4l': BaseComposition(self.bc_nd4l_size, self.bc_nd4l_g, self.bc_nd4l_c, self.bc_nd4l_t, self.bc_nd4l_a, self.bc_nd4l_others),
            'nd5': BaseComposition(self.bc_nd5_size, self.bc_nd5_g, self.bc_nd5_c, self.bc_nd5_t, self.bc_nd5_a, self.bc_nd5_others),
            'nd6': BaseComposition(self.bc_nd6_size, self.bc_nd6_g, self.bc_nd6_c, self.bc_nd6_t, self.bc_nd6_a, self.bc_nd6_others),
            'rRNA_12S': BaseComposition(self.bc_rRNA_12S_size, self.bc_rRNA_12S_g, self.bc_rRNA_12S_c, self.bc_rRNA_12S_t, self.bc_rRNA_12S_a, self.bc_rRNA_12S_others),
            'rRNA_16S': BaseComposition(self.bc_rRNA_16S_size, self.bc_rRNA_16S_g, self.bc_rRNA_16S_c, self.bc_rRNA_16S_t, self.bc_rRNA_16S_a, self.bc_rRNA_16S_others),
        }[type_of_bc]
    
    def set_base_composition(self, type_of_bc, base_composition):
        if type_of_bc=='total_mtDNA':
            (self.bc_total_mtDNA_size, self.bc_total_mtDNA_g, self.bc_total_mtDNA_c, self.bc_total_mtDNA_t, self.bc_total_mtDNA_a, self.bc_total_mtDNA_others) = base_composition.to_raw_data()
        if type_of_bc=='total_pc_mtDNA':
            (self.bc_total_mtDNA_pc_size, self.bc_total_mtDNA_pc_g, self.bc_total_mtDNA_pc_c, self.bc_total_mtDNA_pc_t, self.bc_total_mtDNA_pc_a, self.bc_total_mtDNA_bc_others) = base_composition.to_raw_data()
        if type_of_bc=='d_loop_mtDNA':
            (self.bc_d_loop_size, self.bc_d_loop_g, self.bc_d_loop_c, self.bc_d_loop_t, self.bc_d_loop_a, self.bc_d_loop_others) = base_composition.to_raw_data()
        if type_of_bc=='total_rRNA_mtDNA':
            (self.bc_total_rRNA_size, self.bc_total_rRNA_g, self.bc_total_rRNA_c, self.bc_total_rRNA_t, self.bc_total_rRNA_a, self.bc_total_rRNA_others) = base_composition.to_raw_data()
        if type_of_bc=='atp6':
            (self.bc_atp6_size, self.bc_atp6_g, self.bc_atp6_c, self.bc_atp6_t, self.bc_atp6_a, self.bc_atp6_others) = base_composition.to_raw_data()
        if type_of_bc=='atp8':
            (self.bc_atp8_size, self.bc_atp8_g, self.bc_atp8_c, self.bc_atp8_t, self.bc_atp8_a, self.bc_atp8_others) = base_composition.to_raw_data()
        if type_of_bc=='cox1':
            (self.bc_cox1_size, self.bc_cox1_g, self.bc_cox1_c, self.bc_cox1_t, self.bc_cox1_a, self.bc_cox1_others) = base_composition.to_raw_data()
        if type_of_bc=='cox2':
            (self.bc_cox2_size, self.bc_cox2_g, self.bc_cox2_c, self.bc_cox2_t, self.bc_cox2_a, self.bc_cox2_others) = base_composition.to_raw_data()
        if type_of_bc=='cox3':
            (self.bc_cox3_size, self.bc_cox3_g, self.bc_cox3_c, self.bc_cox3_t, self.bc_cox3_a, self.bc_cox3_others) = base_composition.to_raw_data()
        if type_of_bc=='cytb':
            (self.bc_cytb_size, self.bc_cytb_g, self.bc_cytb_c, self.bc_cytb_t, self.bc_cytb_a, self.bc_cytb_others) = base_composition.to_raw_data()
        if type_of_bc=='nd1':
            (self.bc_nd1_size, self.bc_nd1_g, self.bc_nd1_c, self.bc_nd1_t, self.bc_nd1_a, self.bc_nd1_others) = base_composition.to_raw_data()
        if type_of_bc=='nd2':
            (self.bc_nd2_size, self.bc_nd2_g, self.bc_nd2_c, self.bc_nd2_t, self.bc_nd2_a, self.bc_nd2_others) = base_composition.to_raw_data()
        if type_of_bc=='nd3':
            (self.bc_nd3_size, self.bc_nd3_g, self.bc_nd3_c, self.bc_nd3_t, self.bc_nd3_a, self.bc_nd3_others) = base_composition.to_raw_data()
        if type_of_bc=='nd4':
            (self.bc_nd4_size, self.bc_nd4_g, self.bc_nd4_c, self.bc_nd4_t, self.bc_nd4_a, self.bc_nd4_others) = base_composition.to_raw_data()
        if type_of_bc=='nd4l':
            (self.bc_nd4l_size, self.bc_nd4l_g, self.bc_nd4l_c, self.bc_nd4l_t, self.bc_nd4l_a, self.bc_nd4l_others) = base_composition.to_raw_data()
        if type_of_bc=='nd5':
            (self.bc_nd5_size, self.bc_nd5_g, self.bc_nd5_c, self.bc_nd5_t, self.bc_nd5_a, self.bc_nd5_others) = base_composition.to_raw_data()
        if type_of_bc=='nd6':
            (self.bc_nd6_size, self.bc_nd6_g, self.bc_nd6_c, self.bc_nd6_t, self.bc_nd6_a, self.bc_nd6_others) = base_composition.to_raw_data()
        if type_of_bc=='rRNA_12S':
            (self.bc_rRNA_12S_size, self.bc_rRNA_12S_g, self.bc_rRNA_12S_c, self.bc_rRNA_12S_t, self.bc_rRNA_12S_a, self.bc_rRNA_12S_others) = base_composition.to_raw_data()
        if type_of_bc=='rRNA_16S':
            (self.bc_rRNA_16S_size, self.bc_rRNA_16S_g, self.bc_rRNA_16S_c, self.bc_rRNA_16S_t, self.bc_rRNA_16S_a, self.bc_rRNA_16S_others) = base_composition.to_raw_data()
        
    
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
