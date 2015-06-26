from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.generic.base import TemplateView

from mitoage.analysis.models import MitoAgeEntry, BaseComposition, CodonUsage
from mitoage.taxonomy.models import TaxonomySpecies
from mitoage.taxonomy.utils import BaseCompositionParser, \
    create_dict_advanced_parser, CodonUsageParser


class MitoAgeCodonUsageInline(admin.StackedInline):
    model = CodonUsage
    max_num = 1
    suit_classes = 'suit-tab suit-tab-codon-usage'

class MitoAgeCodonUsageInlinePC(MitoAgeCodonUsageInline):
    fk_name = 'cu_protein_coding_entry'
    verbose_name = 'Codon usage for protein coding'
    exclude = ('cu_atp6_entry','cu_atp8_entry','cu_cox1_entry','cu_cox2_entry','cu_cox3_entry',
               'cu_cytb_entry','cu_nd1_entry','cu_nd2_entry','cu_nd3_entry','cu_nd4_entry','cu_nd4l_entry',
               'cu_nd5_entry','cu_nd6_entry')

class MitoAgeCodonUsageInlineATP6(MitoAgeCodonUsageInline):
    fk_name = 'cu_atp6_entry'
    verbose_name = 'Codon usage for ATP6'
    exclude = ('cu_protein_coding_entry','cu_atp8_entry','cu_cox1_entry','cu_cox2_entry','cu_cox3_entry',
               'cu_cytb_entry','cu_nd1_entry','cu_nd2_entry','cu_nd3_entry','cu_nd4_entry','cu_nd4l_entry',
               'cu_nd5_entry','cu_nd6_entry')

class MitoAgeCodonUsageInlineATP8(MitoAgeCodonUsageInline):
    fk_name = 'cu_atp8_entry'
    verbose_name = 'Codon usage for ATP8'
    exclude = ('cu_protein_coding_entry','cu_atp6_entry','cu_cox1_entry','cu_cox2_entry','cu_cox3_entry',
               'cu_cytb_entry','cu_nd1_entry','cu_nd2_entry','cu_nd3_entry','cu_nd4_entry','cu_nd4l_entry',
               'cu_nd5_entry','cu_nd6_entry')

class MitoAgeCodonUsageInlineCOX1(MitoAgeCodonUsageInline):
    fk_name = 'cu_cox1_entry'
    verbose_name = 'Codon usage for COX1'
    exclude = ('cu_protein_coding_entry','cu_atp6_entry','cu_atp8_entry','cu_cox2_entry','cu_cox3_entry',
               'cu_cytb_entry','cu_nd1_entry','cu_nd2_entry','cu_nd3_entry','cu_nd4_entry','cu_nd4l_entry',
               'cu_nd5_entry','cu_nd6_entry')

class MitoAgeCodonUsageInlineCOX2(MitoAgeCodonUsageInline):
    fk_name = 'cu_cox2_entry'
    verbose_name = 'Codon usage for COX2'
    exclude = ('cu_protein_coding_entry','cu_atp6_entry','cu_atp8_entry','cu_cox1_entry','cu_cox3_entry',
               'cu_cytb_entry','cu_nd1_entry','cu_nd2_entry','cu_nd3_entry','cu_nd4_entry','cu_nd4l_entry',
               'cu_nd5_entry','cu_nd6_entry')

class MitoAgeCodonUsageInlineCOX3(MitoAgeCodonUsageInline):
    fk_name = 'cu_cox3_entry'
    verbose_name = 'Codon usage for COX3'
    exclude = ('cu_protein_coding_entry','cu_atp6_entry','cu_atp8_entry','cu_cox1_entry','cu_cox2_entry',
               'cu_cytb_entry','cu_nd1_entry','cu_nd2_entry','cu_nd3_entry','cu_nd4_entry','cu_nd4l_entry',
               'cu_nd5_entry','cu_nd6_entry')

class MitoAgeCodonUsageInlineCYTB(MitoAgeCodonUsageInline):
    fk_name = 'cu_cytb_entry'
    verbose_name = 'Codon usage for CYTB'
    exclude = ('cu_protein_coding_entry','cu_atp6_entry','cu_atp8_entry','cu_cox1_entry','cu_cox2_entry','cu_cox3_entry',
               'cu_nd1_entry','cu_nd2_entry','cu_nd3_entry','cu_nd4_entry','cu_nd4l_entry',
               'cu_nd5_entry','cu_nd6_entry')

class MitoAgeCodonUsageInlineND1(MitoAgeCodonUsageInline):
    fk_name = 'cu_nd1_entry'
    verbose_name = 'Codon usage for ND1'
    exclude = ('cu_protein_coding_entry','cu_atp6_entry','cu_atp8_entry','cu_cox1_entry','cu_cox2_entry','cu_cox3_entry',
               'cu_cytb_entry','cu_nd2_entry','cu_nd3_entry','cu_nd4_entry','cu_nd4l_entry',
               'cu_nd5_entry','cu_nd6_entry')

class MitoAgeCodonUsageInlineND2(MitoAgeCodonUsageInline):
    fk_name = 'cu_nd2_entry'
    verbose_name = 'Codon usage for ND2'
    exclude = ('cu_protein_coding_entry','cu_atp6_entry','cu_atp8_entry','cu_cox1_entry','cu_cox2_entry','cu_cox3_entry',
               'cu_cytb_entry','cu_nd1_entry','cu_nd3_entry','cu_nd4_entry','cu_nd4l_entry',
               'cu_nd5_entry','cu_nd6_entry')

class MitoAgeCodonUsageInlineND3(MitoAgeCodonUsageInline):
    fk_name = 'cu_nd3_entry'
    verbose_name = 'Codon usage for ND3'
    exclude = ('cu_protein_coding_entry','cu_atp6_entry','cu_atp8_entry','cu_cox1_entry','cu_cox2_entry','cu_cox3_entry',
               'cu_cytb_entry','cu_nd1_entry','cu_nd2_entry','cu_nd4_entry','cu_nd4l_entry',
               'cu_nd5_entry','cu_nd6_entry')

class MitoAgeCodonUsageInlineND4(MitoAgeCodonUsageInline):
    fk_name = 'cu_nd4_entry'
    verbose_name = 'Codon usage for ND4'
    exclude = ('cu_protein_coding_entry','cu_atp6_entry','cu_atp8_entry','cu_cox1_entry','cu_cox2_entry','cu_cox3_entry',
               'cu_cytb_entry','cu_nd1_entry','cu_nd2_entry','cu_nd3_entry','cu_nd4l_entry',
               'cu_nd5_entry','cu_nd6_entry')

class MitoAgeCodonUsageInlineND4L(MitoAgeCodonUsageInline):
    fk_name = 'cu_nd4l_entry'
    verbose_name = 'Codon usage for ND4L'
    exclude = ('cu_protein_coding_entry','cu_atp6_entry','cu_atp8_entry','cu_cox1_entry','cu_cox2_entry','cu_cox3_entry',
               'cu_cytb_entry','cu_nd1_entry','cu_nd2_entry','cu_nd3_entry','cu_nd4_entry',
               'cu_nd5_entry','cu_nd6_entry')

class MitoAgeCodonUsageInlineND5(MitoAgeCodonUsageInline):
    fk_name = 'cu_nd5_entry'
    verbose_name = 'Codon usage for ND5'
    exclude = ('cu_protein_coding_entry','cu_atp6_entry','cu_atp8_entry','cu_cox1_entry','cu_cox2_entry','cu_cox3_entry',
               'cu_cytb_entry','cu_nd1_entry','cu_nd2_entry','cu_nd3_entry','cu_nd4_entry','cu_nd4l_entry',
               'cu_nd6_entry')

class MitoAgeCodonUsageInlineND6(MitoAgeCodonUsageInline):
    fk_name = 'cu_nd6_entry'
    verbose_name = 'Codon usage for ND6'
    exclude = ('cu_protein_coding_entry','cu_atp6_entry','cu_atp8_entry','cu_cox1_entry','cu_cox2_entry','cu_cox3_entry',
               'cu_cytb_entry','cu_nd1_entry','cu_nd2_entry','cu_nd3_entry','cu_nd4_entry','cu_nd4l_entry',
               'cu_nd5_entry')


################################### MitoAge entry admin ###################################
class MitoAgeEntryAdmin(ModelAdmin):
    list_display = ('entry_summary', 'species')
    suit_form_tabs = (('general', 'General'), ('base-composition', 'Base composition - general'), ('base-composition-genes', 'Base composition - genes'), ('codon-usage', 'Codon usage'))
    readonly_fields = ['common_name', 'lifespan', 'link_to_hagr']
    inlines = [MitoAgeCodonUsageInlinePC, MitoAgeCodonUsageInlineATP6, MitoAgeCodonUsageInlineATP8, MitoAgeCodonUsageInlineCOX1,
               MitoAgeCodonUsageInlineCOX2,MitoAgeCodonUsageInlineCOX3,MitoAgeCodonUsageInlineCYTB,MitoAgeCodonUsageInlineND1,
               MitoAgeCodonUsageInlineND2,MitoAgeCodonUsageInlineND3,MitoAgeCodonUsageInlineND4,MitoAgeCodonUsageInlineND4L,
               MitoAgeCodonUsageInlineND5,MitoAgeCodonUsageInlineND6]

    fieldsets = (
        ('General', {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': ('species', 'common_name', 'lifespan', 'link_to_hagr')
        }),
                 
                 
        ('Total mtDNA', {
            'classes': ('suit-tab', 'suit-tab-base-composition',),
            'fields': ('bc_total_mtDNA_size', 'bc_total_mtDNA_g', 'bc_total_mtDNA_c', 'bc_total_mtDNA_a', 'bc_total_mtDNA_t', 'bc_total_mtDNA_others')
        }),
        ('Total protein-coding mtDNA', {
            'classes': ('suit-tab', 'suit-tab-base-composition',),
            'fields': ('bc_total_mtDNA_pc_size', 'bc_total_mtDNA_pc_g', 'bc_total_mtDNA_pc_c', 'bc_total_mtDNA_pc_a', 'bc_total_mtDNA_pc_t', 'bc_total_mtDNA_bc_others')
        }),
        ('D-loop region of mtDNA', {
            'classes': ('suit-tab', 'suit-tab-base-composition',),
            'fields': ('bc_d_loop_size', 'bc_d_loop_g', 'bc_d_loop_c', 'bc_d_loop_a', 'bc_d_loop_t', 'bc_d_loop_others')
        }),
        ('Total ribosomal RNA-coding mtDNA', {
            'classes': ('suit-tab', 'suit-tab-base-composition',),
            'fields': ('bc_total_rRNA_size', 'bc_total_rRNA_g', 'bc_total_rRNA_c', 'bc_total_rRNA_a', 'bc_total_rRNA_t', 'bc_total_rRNA_others')
        }),
        ('Gene ATP6', {
            'classes': ('suit-tab', 'suit-tab-base-composition-genes',),
            'fields': ('bc_atp6_size', 'bc_atp6_g', 'bc_atp6_c', 'bc_atp6_a', 'bc_atp6_t', 'bc_atp6_others')
        }),
        ('Gene ATP8', {
            'classes': ('suit-tab', 'suit-tab-base-composition-genes',),
            'fields': ('bc_atp8_size', 'bc_atp8_g', 'bc_atp8_c', 'bc_atp8_a', 'bc_atp8_t', 'bc_atp8_others')
        }),
        ('Gene COX1', {
            'classes': ('suit-tab', 'suit-tab-base-composition-genes',),
            'fields': ('bc_cox1_size', 'bc_cox1_g', 'bc_cox1_c', 'bc_cox1_a', 'bc_cox1_t', 'bc_cox1_others')
        }),
        ('Gene COX2', {
            'classes': ('suit-tab', 'suit-tab-base-composition-genes',),
            'fields': ('bc_cox2_size', 'bc_cox2_g', 'bc_cox2_c', 'bc_cox2_a', 'bc_cox2_t', 'bc_cox2_others')
        }),
        ('Gene COX3', {
            'classes': ('suit-tab', 'suit-tab-base-composition-genes',),
            'fields': ('bc_cox3_size', 'bc_cox3_g', 'bc_cox3_c', 'bc_cox3_a', 'bc_cox3_t', 'bc_cox3_others')
        }),
        ('Gene CYTB', {
            'classes': ('suit-tab', 'suit-tab-base-composition-genes',),
            'fields': ('bc_cytb_size', 'bc_cytb_g', 'bc_cytb_c', 'bc_cytb_a', 'bc_cytb_t', 'bc_cytb_others')
        }),
        ('Gene ND1', {
            'classes': ('suit-tab', 'suit-tab-base-composition-genes',),
            'fields': ('bc_nd1_size', 'bc_nd1_g', 'bc_nd1_c', 'bc_nd1_a', 'bc_nd1_t', 'bc_nd1_others')
        }),
        ('Gene ND2', {
            'classes': ('suit-tab', 'suit-tab-base-composition-genes',),
            'fields': ('bc_nd2_size', 'bc_nd2_g', 'bc_nd2_c', 'bc_nd2_a', 'bc_nd2_t', 'bc_nd2_others')
        }),
        ('Gene ND3', {
            'classes': ('suit-tab', 'suit-tab-base-composition-genes',),
            'fields': ('bc_nd3_size', 'bc_nd3_g', 'bc_nd3_c', 'bc_nd3_a', 'bc_nd3_t', 'bc_nd3_others')
        }),
        ('Gene ND4', {
            'classes': ('suit-tab', 'suit-tab-base-composition-genes',),
            'fields': ('bc_nd4_size', 'bc_nd4_g', 'bc_nd4_c', 'bc_nd4_a', 'bc_nd4_t', 'bc_nd4_others')
        }),
        ('Gene ND4L', {
            'classes': ('suit-tab', 'suit-tab-base-composition-genes',),
            'fields': ('bc_nd4l_size', 'bc_nd4l_g', 'bc_nd4l_c', 'bc_nd4l_a', 'bc_nd4l_t', 'bc_nd4l_others')
        }),
        ('Gene ND5', {
            'classes': ('suit-tab', 'suit-tab-base-composition-genes',),
            'fields': ('bc_nd5_size', 'bc_nd5_g', 'bc_nd5_c', 'bc_nd5_a', 'bc_nd5_t', 'bc_nd5_others')
        }),
        ('Gene ND6', {
            'classes': ('suit-tab', 'suit-tab-base-composition-genes',),
            'fields': ('bc_nd6_size', 'bc_nd6_g', 'bc_nd6_c', 'bc_nd6_a', 'bc_nd6_t', 'bc_nd6_others')
        }),
        ('rRNA 12S subunit-coding region', {
            'classes': ('suit-tab', 'suit-tab-base-composition-genes',),
            'fields': ('bc_rRNA_12S_size', 'bc_rRNA_12S_g', 'bc_rRNA_12S_c', 'bc_rRNA_12S_a', 'bc_rRNA_12S_t', 'bc_rRNA_12S_others')
        }),
        ('rRNA 16S subunit-coding region', {
            'classes': ('suit-tab', 'suit-tab-base-composition-genes',),
            'fields': ('bc_rRNA_16S_size', 'bc_rRNA_16S_g', 'bc_rRNA_16S_c', 'bc_rRNA_16S_a', 'bc_rRNA_16S_t', 'bc_rRNA_16S_others')
        }),
    )

    ########## Add additional urls in the admin ###############
    def get_urls(self):
        urls = super(MitoAgeEntryAdmin, self).get_urls()
        extra_urls = [
            #url(r'^todo/$', TemplateView.as_view(template_name="admin/todo.html"), name='todo_list'),
            # not advisable to use the above, unless it is a public page (no login verification)
            url(r'^todo/$', self.admin_site.admin_view(self.todo), name='todo_list'),
            url(r'^import/base_composition/$', self.admin_site.admin_view(self.bc_import), name='bc_csvimport'),
            url(r'^import/base_composition/complete$', self.admin_site.admin_view(self.bc_import_complete), name='bc_csvimportcomplete'),
            url(r'^import/codon_usage/$', self.admin_site.admin_view(self.cu_import), name='cu_csvimport'),
            url(r'^import/codon_usage/complete$', self.admin_site.admin_view(self.cu_import_complete), name='cu_csvimportcomplete'),
        ]
        return extra_urls + urls
    
    def todo(self, request):
        return render_to_response('admin/todo.html', locals())

    def bc_import(self, request):

        if len(request.FILES) > 0:
            csvfile = request.FILES['bc_file']
            filename = csvfile.name
            
            bc_section = request.POST['bc_section']
            if not bc_section in MitoAgeEntry.get_bc_sections():
                # incorrect columns
                title, include_example, include_input, error_type = "Base composition upload error - wrong section selection", False, False, "wrong section"
                return render_to_response('admin/base_composition_validation.html', locals(), RequestContext(request))
            
            # Call where we already have a file; processing data 
            bcp = BaseCompositionParser(create_dict_advanced_parser(csvfile))
            
            if bcp.mismatched_columns:
                # incorrect columns
                title, include_example, include_input, error_type = "Base composition upload error - Incorrect columns", True, False, "wrong columns"
                return render_to_response('admin/base_composition_validation.html', locals(), RequestContext(request))
            
            # column headers are correct
            (errors, duplicates, ignored) = bcp.validate_all()
            # although ignored is not required for AnAge uploads - nothing can be ignored
            
            if errors:
                # inconsistent lines in input
                title, include_example, include_input, error_type = "Base composition upload error - wrong format and inconsistent entries in the uploaded file", False, True, "wrong format or inconsistent columns"
                return render_to_response('admin/base_composition_validation.html', locals(), RequestContext(request))

            # input file is correct - what remains is to check against the database
            (db_errors, already_in_db, consistent_changes) = bcp.validate_against_database(bc_section)
            
            if db_errors:
                # clashes with the database
                title, include_example, include_input, error_type = "Base composition upload error - lifespan or HAGR ID inconsistent with already existing values in database", False, True, "clashes_with_db"
                return render_to_response('admin/base_composition_validation.html', locals(), RequestContext(request))
            
            # No significant errors or clashes - we can proceed with the upload
            # Confirmation screen with the changes that will be made, duplicates and already in DB can also be displayed
            title, include_example, include_input, error_type = "Parsing successful. You may proceed with the upload.", False, False, "no_significant_errors"
            
            # preparing data to send forward; we are interested in new_entries_to_be_added and in ignored
            list_of_entries = []
            
            for row in consistent_changes:
                list_of_entries.append({'Species':row[0]['Species'], 'G':row[0]['G'], 'C':row[0]['C'], 'A':row[0]['A'], 'T':row[0]['T'], 'Other':row[0]['Other'], 'mtDNA size (bp)':row[0]['mtDNA size (bp)']})
                
            # dumping, "json-ing", optionally zipping      
            import zlib, json
            data = json.dumps(list_of_entries)  # data is sent entirely, but next time processing will result in silent errors (if any). 

            return render_to_response('admin/base_composition_validation.html', locals(), RequestContext(request))
        return render_to_response('admin/base_composition_import.html', locals(), RequestContext(request))


    def bc_import_complete(self, request):
        import json
        data = json.loads(request.POST['data'])

        bc_section = request.POST['section']
        if not bc_section in MitoAgeEntry.get_bc_sections():
            # incorrect columns
            title, include_example, include_input, error_type = "Base composition upload error - wrong section selection", False, False, "wrong section"
            return render_to_response('admin/base_composition_validation.html', locals(), RequestContext(request))

        message = ""        
        # creating species objects; all entries should be new (otherwise they were duplicates or clashing with the DB)
        processed_species = []
        for entry in data:
            # silently skipping None and empty string
            if ((not entry["Species"]) or entry["Species"].strip()==""):
                continue
            
            # silently removing duplicates from input
            # will assume no tempering has occurred with the data, and hence first come will be first saved (duplicates will be ignored)
            if entry["Species"] in processed_species:
                continue
            processed_species.append(entry["Species"])
            
            # checking however that:
            #     the DB does have the current species already (otherwise it was deleted or tempered with)
            try:
                g = int(entry['G'])
                c = int(entry['C'])
                a = int(entry['A'])
                t = int(entry['T'])
                size = int(entry['mtDNA size (bp)'])
                other = int(entry['Other'])
                input_base_composition = BaseComposition(size, g, c, a, t, other)
                                         
                try:
                    current_species = TaxonomySpecies.objects.get(name=entry["Species"])
                    mitoage_entry, created = MitoAgeEntry.objects.get_or_create(species = current_species)

                    base_composition = mitoage_entry.get_base_composition(bc_section)
                        
                    if base_composition.is_empty():
                        mitoage_entry.set_base_composition(bc_section, input_base_composition)
                        mitoage_entry.save()
                        message += "<li>Species \"%s\" saved. <br/></li>" % entry["Species"]
                    elif not base_composition.is_same(input_base_composition):
                        message += "<li class='alert alert-warning'>Species %s already exists, however recorded base composition for section %s is different. Either somebody has just added the data at the same time as you (well... to be more exact, just after you uploaded your file), you refreshed the page, or you are trying to temper with the data. It's probably the first one though... ;) ... ignoring error (this time!). </li>" % (entry['Species'], bc_section)
                    # else, silently failing as it is already in the database
                except TaxonomySpecies.DoesNotExist:
                    message += "<li class='alert alert-warning'>Species \"%s\" is not in the database. Either somebody has deleted this species at the same time as you (well... to be more exact, just after you uploaded your file), or you are trying to temper with the data. It's probably the first one though... ;) ... ignoring error (this time!). <br/></li>" % entry["Species"]
                
            except ValueError:
                message += "<li class='alert alert-danger'>Input values for species %s need to be numbers. Please stop tempering with the data. <br/></li>" % entry['Species']
        
        return render_to_response('admin/import_complete.html', locals(), RequestContext(request))


    def cu_import(self, request):

        cup_columns = CodonUsageParser.get_codon_usage_fields()
        
        if len(request.FILES) > 0:
            csvfile = request.FILES['cu_file']
            filename = csvfile.name
            
            cu_section = request.POST['cu_section']
            if not cu_section in MitoAgeEntry.get_cu_sections():
                # incorrect columns
                title, include_example, include_input, error_type = "Codon usage upload error - wrong section selection", False, False, "wrong section"
                return render_to_response('admin/codon_usage_validation.html', locals(), RequestContext(request))
            
            # Call where we already have a file; processing data 
            cup = CodonUsageParser(create_dict_advanced_parser(csvfile))
            
            if cup.mismatched_columns:
                # incorrect columns
                title, include_example, include_input, error_type = "Codon usage upload error - Incorrect columns", True, False, "wrong columns"
                return render_to_response('admin/codon_usage_validation.html', locals(), RequestContext(request))
            
            # column headers are correct
            (errors, duplicates, ignored) = cup.validate_all()
            # although ignored is not required for AnAge uploads - nothing can be ignored
            
            if errors:
                # inconsistent lines in input
                title, include_example, include_input, error_type = "Codon usage upload error - wrong format and inconsistent entries in the uploaded file", False, True, "wrong format or inconsistent columns"
                return render_to_response('admin/codon_usage_validation.html', locals(), RequestContext(request))

            # input file is correct - what remains is to check against the database
            (db_errors, already_in_db, consistent_changes) = cup.validate_against_database(cu_section)
            
            if db_errors:
                # clashes with the database
                title, include_example, include_input, error_type = "Codon usage upload error - lifespan or HAGR ID inconsistent with already existing values in database", False, True, "clashes_with_db"
                return render_to_response('admin/codon_usage_validation.html', locals(), RequestContext(request))
            
            # No significant errors or clashes - we can proceed with the upload
            # Confirmation screen with the changes that will be made, duplicates and already in DB can also be displayed
            title, include_example, include_input, error_type = "Parsing successful. You may proceed with the upload.", False, False, "no_significant_errors"
            
            # preparing data to send forward; we are interested in new_entries_to_be_added and in ignored
            list_of_entries = []
            
            for row in consistent_changes:
                new_dict = {}
                for field_name in CodonUsageParser.get_codon_usage_fields():
                    new_dict[field_name]=row[0][field_name]
                list_of_entries.append(new_dict)
                
            # dumping, "json-ing", optionally zipping      
            import zlib, json
            data = json.dumps(list_of_entries)  # data is sent entirely, but next time processing will result in silent errors (if any). 

            return render_to_response('admin/codon_usage_validation.html', locals(), RequestContext(request))
        return render_to_response('admin/codon_usage_import.html', locals(), RequestContext(request))


    def cu_import_complete(self, request):
        import json
        data = json.loads(request.POST['data'])

        cu_section = request.POST['section']
        if not cu_section in MitoAgeEntry.get_cu_sections():
            # incorrect columns
            title, include_example, include_input, error_type = "Codon usage upload error - wrong section selection", False, False, "wrong section"
            return render_to_response('admin/codon_usage_validation.html', locals(), RequestContext(request))

        message = ""        
        # creating species objects; all entries should be new (otherwise they were duplicates or clashing with the DB)
        processed_species = []
        for entry in data:
            # silently skipping None and empty string
            if ((not entry["Species"]) or entry["Species"].strip()==""):
                continue
            
            # silently removing duplicates from input
            # will assume no tempering has occurred with the data, and hence first come will be first saved (duplicates will be ignored)
            if entry["Species"] in processed_species:
                continue
            processed_species.append(entry["Species"])
            
            # checking however that:
            #     the DB does have the current species already (otherwise it was deleted or tempered with)
            try:
                input_codon_usage = CodonUsage()
                input_codon_usage.set_codon_usage_from_dictionary(entry)
                input_codon_usage.aa = entry['Amino Acids']
                input_codon_usage.size = entry['mtDNA size (bp)']
                                         
                try:
                    current_species = TaxonomySpecies.objects.get(name=entry["Species"])
                    mitoage_entry, created = MitoAgeEntry.objects.get_or_create(species = current_species)

                    codon_usage = mitoage_entry.get_codon_usage(cu_section)
                        
                    if codon_usage == None:
                        # saving here is done through the codon_usage object
                        mitoage_entry.set_codon_usage(cu_section, input_codon_usage)
                        input_codon_usage.save()
                        #mitoage_entry.save()
                        
                        message += "<li>Species \"%s\" saved. <br/></li>" % entry["Species"]
                    elif not codon_usage.same_values(codon_usage):
                        message += "<li class='alert alert-warning'>Species %s already exists, however recorded codon usage for section %s is different. Either somebody has just added the data at the same time as you (well... to be more exact, just after you uploaded your file), you refreshed the page, or you are trying to temper with the data. It's probably the first one though... ;) ... ignoring error (this time!). </li>" % (entry['Species'], cu_section)
                    # else, silently failing as it is already in the database
                except TaxonomySpecies.DoesNotExist:
                    message += "<li class='alert alert-warning'>Species \"%s\" is not in the database. Either somebody has deleted this species at the same time as you (well... to be more exact, just after you uploaded your file), or you are trying to temper with the data. It's probably the first one though... ;) ... ignoring error (this time!). <br/></li>" % entry["Species"]
                
            except ValueError:
                message += "<li class='alert alert-danger'>Input values for species %s need to be numbers. Please stop tempering with the data. <br/></li>" % entry['Species']
        
        return render_to_response('admin/import_complete.html', locals(), RequestContext(request))
        

    ########## Additional functions with info for the general panel ###############
    def entry_summary(self, obj):
        return u'mtDNA analysis for %s' % obj.species.name 
    entry_summary.short_description = "MitoAge entry"

    def common_name(self, obj):
        return u'%s' % obj.species.common_name
    common_name.short_description = "Species' common name"

    def lifespan(self, obj):
        return u'%s' % (obj.species.lifespan if obj.species.lifespan else "Not recorded")
    lifespan.short_description = 'Maximum lifespan'

    def link_to_hagr(self, obj):
        return u'<a href="http://genomics.senescence.info/species/query.php?search=%s">%s@AnAge</a>' % (obj.species.hagr_id, obj.species.name) 
    link_to_hagr.short_description = 'Link to AnAge'
    link_to_hagr.allow_tags = True


################################### Register all admin classes ###################################
#admin.site.register(BaseComposition, BaseCompositionAdmin)
admin.site.register(MitoAgeEntry, MitoAgeEntryAdmin)
