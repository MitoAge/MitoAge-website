from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.shortcuts import render, render_to_response
from django.template.context import RequestContext

from mitoage.taxonomy.models import TaxonomyClass, TaxonomyOrder, TaxonomyFamily, TaxonomySpecies
from mitoage.taxonomy.utils import TaxonomyParser, AnAgeParser, \
    create_dict_advanced_parser


################################### Class admin ###################################
class TaxonomyClassAdmin(ModelAdmin):
    list_display = ('displayed_class',)
    
    def displayed_class(self, obj):
        return obj.name
    displayed_class.short_description = 'Class'
    displayed_class.admin_order_field = 'name'


################################### Order admin ###################################
class TaxonomyOrderAdmin(ModelAdmin):
    list_display = ('displayed_order', 'displayed_class')

    def displayed_order(self, obj):
        return obj.name
    displayed_order.short_description = 'Order'
    displayed_order.admin_order_field = 'name'

    def displayed_class(self, obj):
        if not obj.taxonomy_class:
            return u'No class assigned' 
        return u'<a href="%s">%s</a>' % (obj.taxonomy_class.get_absolute_admin_url(), obj.taxonomy_class.name) 
    displayed_class.short_description = 'Class'
    displayed_class.admin_order_field = 'taxonomy_class__name'
    displayed_class.allow_tags = True


################################### Family admin ###################################
class TaxonomyFamilyAdmin(ModelAdmin):
    list_display = ('displayed_family', 'displayed_order', 'displayed_class')

    def displayed_family(self, obj):
        return obj.name
    displayed_family.short_description = 'Family'
    displayed_family.admin_order_field = 'name'

    def displayed_order(self, obj):
        if not obj.taxonomy_order:
            return u'No order assigned' 
        return u'<a href="%s">%s</a>' % (obj.taxonomy_order.get_absolute_admin_url(), obj.taxonomy_order.name) 
    displayed_order.short_description = 'Order'
    displayed_order.admin_order_field = 'taxonomy_order__name'
    displayed_order.allow_tags = True

    def displayed_class(self, obj):
        if not obj.taxonomy_order:
            return u'No order assigned' 
        if not obj.taxonomy_order.taxonomy_class:
            return u'No class assigned' 
        return u'<a href="%s">%s</a>' % (obj.taxonomy_order.taxonomy_class.get_absolute_admin_url(), obj.taxonomy_order.taxonomy_class.name) 
    displayed_class.short_description = 'Class'
    displayed_class.admin_order_field = 'taxonomy_order__taxonomy_class__name'
    displayed_class.allow_tags = True


################################### Species admin ###################################
class TaxonomySpeciesAdmin(ModelAdmin):
    list_display = ('displayed_species', 'displayed_common_name', 'displayed_family', 'displayed_order', 'displayed_class')
    list_filter = ('taxonomy_family__name', 'taxonomy_family__taxonomy_order__name', 'taxonomy_family__taxonomy_order__taxonomy_class__name', )
    search_fields = ('name', )

    # adding to list_display 'lifespan' results in messing css code
        
    # <th scope="col" class="lifespan-column sortable column-lifespan">        <==== this is the th in the html
    # should be changeable through css
    
    def displayed_species(self, obj):
        return obj.name
    displayed_species.short_description = 'Species'
    displayed_species.admin_order_field = 'name'

    def displayed_common_name(self, obj):
        if not obj.common_name:
            return u'No common name assigned' 
        return u'%s' % obj.common_name
    displayed_common_name.short_description = 'Common name'
    displayed_common_name.admin_order_field = 'common_name'

    def displayed_family(self, obj):
        if not obj.taxonomy_family:
            return u'No family assigned' 
        return u'<a href="%s">%s</a>' % (obj.taxonomy_family.get_absolute_admin_url(), obj.taxonomy_family.name)
    displayed_family.short_description = 'Family'
    displayed_family.admin_order_field = 'name'
    displayed_family.allow_tags = True

    def displayed_order(self, obj):
        if not obj.taxonomy_family:
            return u'No family assigned' 
        if not obj.taxonomy_family.taxonomy_order:
            return u'No order assigned' 
        return u'<a href="%s">%s</a>' % (obj.taxonomy_family.taxonomy_order.get_absolute_admin_url(), obj.taxonomy_family.taxonomy_order.name) 
    displayed_order.short_description = 'Order'
    displayed_order.admin_order_field = 'taxonomy_order__name'
    displayed_order.allow_tags = True

    def displayed_class(self, obj):
        if not obj.taxonomy_family:
            return u'No family assigned' 
        if not obj.taxonomy_family.taxonomy_order:
            return u'No order assigned' 
        if not obj.taxonomy_family.taxonomy_order.taxonomy_class:
            return u'No class assigned' 
        return u'<a href="%s">%s</a>' % (obj.taxonomy_family.taxonomy_order.taxonomy_class.get_absolute_admin_url(), obj.taxonomy_family.taxonomy_order.taxonomy_class.name) 
    displayed_class.short_description = 'Class'
    displayed_class.admin_order_field = 'taxonomy_order__taxonomy_class__name'
    displayed_class.allow_tags = True


    ########## Add additional urls in the admin ###############
    def get_urls(self):
        urls = super(TaxonomySpeciesAdmin, self).get_urls()
        extra_urls = [
            url(r'^import/$', self.admin_site.admin_view(self.taxonomy_import), name='taxonomy_csvimport'),
            url(r'^import/complete$', self.admin_site.admin_view(self.taxonomy_import_complete), name='taxonomy_csvimportcomplete'),
            url(r'^import/anage/$', self.admin_site.admin_view(self.anage_import), name='anage_csvimport'),
            url(r'^import/anage/complete$', self.admin_site.admin_view(self.anage_import_complete), name='anage_csvimportcomplete'),
        ]
        return extra_urls + urls

    def anage_import(self, request):

        if len(request.FILES) > 0:
            csvfile = request.FILES['anage_file']
            filename = csvfile.name
            
            # Call where we already have a file; processing data 
            ap = AnAgeParser(create_dict_advanced_parser(csvfile))
            
            if ap.mismatched_columns:
                # incorrect columns
                title, include_example, include_input, error_type = "AnAge upload error - Incorrect columns", True, False, "wrong columns"
                return render_to_response('admin/anage_validation.html', locals(), RequestContext(request))
            
            # column headers are correct
            (errors, duplicates, ignored) = ap.validate_all()
            # although ignored is not required for AnAge uploads - nothing can be ignored
            
            if errors:
                # inconsistent lines in input
                title, include_example, include_input, error_type = "AnAge upload error - wrong format and inconsistent entries in the uploaded file", False, True, "wrong format or inconsistent columns"
                return render_to_response('admin/anage_validation.html', locals(), RequestContext(request))

            # input file is correct - what remains is to check against the database
            (db_errors, already_in_db, consistent_changes) = ap.validate_against_database()
            
            if db_errors:
                # clashes with the database
                title, include_example, include_input, error_type = "AnAge upload error - lifespan or HAGR ID inconsistent with already existing values in database", False, True, "clashes_with_db"
                return render_to_response('admin/anage_validation.html', locals(), RequestContext(request))
            
            # No significant errors or clashes - we can proceed with the upload
            # Confirmation screen with the changes that will be made, duplicates and already in DB can also be displayed
            title, include_example, include_input, error_type = "Parsing successful. You may proceed with the upload.", False, False, "no_significant_errors"
            
            # preparing data to send forward; we are interested in new_entries_to_be_added and in ignored        
            list_of_entries = []
            for row in consistent_changes:
                list_of_entries.append({'Species':row[0]['Species'], 'Lifespan':row[0]['Lifespan'], 'HAGRID':row[0]['HAGRID']})
                
            # dumping, "json-ing", optionally zipping      
            import zlib, json
            data = json.dumps(list_of_entries)  # data is sent entirely, but next time processing will result in silent errors (if any). 

            return render_to_response('admin/anage_validation.html', locals(), RequestContext(request))
        
        return render_to_response('admin/anage_import.html', locals(), RequestContext(request))

    def anage_import_complete(self, request):
        import json
        data = json.loads(request.POST['data'])

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
            
            # checking however that the DB does have the current species already (otherwise it was deleted or tempered with)
            try:
                ls = float(entry['Lifespan'])
                hagr_id = int(entry['HAGRID'])
                try:
                    existing_species = TaxonomySpecies.objects.get(name=entry["Species"])
                    if not existing_species.lifespan and not existing_species.hagr_id:
                        existing_species.lifespan = ls
                        existing_species.hagr_id = hagr_id
                        existing_species.save()
                        message += "<li>Species \"%s\" saved. <br/></li>" % entry["Species"]
                    elif existing_species.lifespan != ls or existing_species.hagr_id != hagr_id:
                        message += "<li class='alert alert-warning'>Species %s already exists, however recorded lifespan and/or HAGR ID are different. Either somebody has just added the data at the same time as you (well... to be more exact, just after you uploaded your file), you refreshed the page, or you are trying to temper with the data. It's probably the first one though... ;) ... ignoring error (this time!). </li>" % entry['Species']
                    # else, silently failing.
                except TaxonomySpecies.DoesNotExist:
                    message += "<li class='alert alert-warning'>Species \"%s\" is not in the database. Either somebody has deleted this species at the same time as you (well... to be more exact, just after you uploaded your file), or you are trying to temper with the data. It's probably the first one though... ;) ... ignoring error (this time!). <br/></li>" % entry["Species"]
                
            except ValueError:
                message += "<li class='alert alert-danger'>Input lifespan and HAGR ID values for species %s need to be numbers. Please stop tempering with the data. <br/></li>" % entry['Species']
        
        return render_to_response('admin/import_complete.html', locals(), RequestContext(request))

    
    ########## Taxonomy bulk import ###############
    def taxonomy_import(self, request):
        app_label = 'Taxonomy'
        if len(request.FILES) > 0:
            csvfile = request.FILES['taxonomy_file']
            filename = csvfile.name
            
            # Call where we already have a file; processing data
            tp = TaxonomyParser( create_dict_advanced_parser(csvfile) )
                
            if tp.mismatched_columns:
                # incorrect columns
                title, include_example, include_input, error_type = "Taxonomy upload error - Incorrect columns", True, False, "wrong columns"
                return render_to_response('admin/taxonomy_validation.html', locals(), RequestContext(request))
            
            # column headers are correct
            (errors, duplicates, ignored) = tp.validate_all()
    
            if errors:
                # inconsistent lines in input
                title, include_example, include_input, error_type = "Taxonomy upload error - wrong format and inconsistent entries in the uploaded file", False, True, "wrong format or inconsistent columns"
                return render_to_response('admin/taxonomy_validation.html', locals(), RequestContext(request))
                    
            # input file is correct - what remains is to check against the database
            # should also report duplicates and ignored on the next screen but they will be ignored
            tp.validate_against_database()
            db_errors =  tp.upload_validation_category[2]+tp.upload_validation_category[5]
            already_in_db = tp.upload_validation_category[1]
            # incomplete entries category[3] are already caught in ignored by the input_consistency_check function
            #incomplete = tp.upload_validation_category[3]
                
            if db_errors:
                # clashes with the database
                title, include_example, include_input, error_type = "Taxonomy upload error - input lines inconsistent with database entries", False, True, "clashes_with_db"
                return render_to_response('admin/taxonomy_validation.html', locals(), RequestContext(request))
                
            # No significant errors or clashes - we can proceed with the upload
            # Confirmation screen with the changes that will be made, duplicates, ignored (from both tests) can also be displayed
            title, include_example, include_input, error_type = "Parsing successful. You may proceed with the upload.", False, False, "no_significant_errors"
            new_entries_to_be_added = tp.upload_validation_category[4]
            ignored = tp.remove_warnings_for_already_in_db(ignored)

            # preparing data to send forward; we are interested in new_entries_to_be_added and in ignored        
            list_of_entries = []
            for row in new_entries_to_be_added:
                list_of_entries.append({'Species':row[0].name, 'Family':row[0].taxonomy_family.name, 'Order':row[0].taxonomy_family.taxonomy_order.name, 'Class':row[0].taxonomy_family.taxonomy_order.taxonomy_class.name, 'Common name':row[0].common_name })
            for row in ignored:
                list_of_entries.append({'Species':row.entry['Species'], 'Family':row.entry['Family'], 'Order':row.entry['Order'], 'Class':row.entry['Class'], 'Common name':row.entry['Common name']})
                
            # dumping, "json-ing", optionally zipping      
            import zlib, json
            data = json.dumps(list_of_entries)  # next time processing will result in silent errors (if any). 
            #data = zlib.compress(data, 9)
                
            return render_to_response('admin/taxonomy_validation.html', locals(), RequestContext(request))
        
        # Initial call - display form for upload
        title = 'Import taxonomy entries into MitoAge'
        return render_to_response('admin/taxonomy_import.html', locals(), RequestContext(request))
    
    def taxonomy_import_complete(self, request):
        
        import json, zlib
        #data = json.loads(zlib.decompress(request.POST['data']))
        data = json.loads(request.POST['data'])

        message = ""
        # creating species objects; all entries should be new (otherwise they were duplicates or clashing with the DB)
        processed_species = {} 
        for entry in data:
            # silently skipping None and empty string
            if ((not entry["Species"]) or entry["Species"]==""):
                continue
            
            # silently removing duplicates from input
            # will assume no tempering has occurred with the data, and hence first come will be first saved (duplicates will be ignored)
            if entry["Species"] in processed_species:
                continue
            processed_species[entry["Species"]] = TaxonomySpecies.create_new_species(entry["Species"], entry["Family"], entry["Order"], entry["Class"], entry["Common name"], True)

            # checking however that the DB doesn't have the current species already (shouldn't happen)
            try:
                existing_species = TaxonomySpecies.objects.get(name=entry["Species"])
                message += "<li class='alert alert-warning'>Species \"%s\" is already in the database. Either somebody has uploaded this species at the same time as you (well... to be more exact, just after you uploaded your file), you refreshed the page, or you are trying to temper with the data. It's probably the first one though... ;) ... ignoring error (this time!). </li>" % entry["Species"]
            except TaxonomySpecies.DoesNotExist:
                processed_species[entry["Species"]].save()
                message += "<li>Species \"%s\" saved. </li>" % entry["Species"]
        
        return render_to_response('admin/import_complete.html', locals(), RequestContext(request))


################################### Register all admin classes ###################################
admin.site.register(TaxonomyClass, TaxonomyClassAdmin)
admin.site.register(TaxonomyOrder, TaxonomyOrderAdmin)
admin.site.register(TaxonomyFamily, TaxonomyFamilyAdmin)
admin.site.register(TaxonomySpecies, TaxonomySpeciesAdmin)
