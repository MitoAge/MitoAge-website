from django.core import urlresolvers
from django.db import models, transaction

class ClickableTaxonomyModel(models.Model):
    class Meta: 
        abstract = True
        
    def get_absolute_admin_url(self):
        return urlresolvers.reverse("admin:%s_%s_change" % (self._meta.app_label, self._meta.module_name), args=(self.id,))


class TaxonomyClass(ClickableTaxonomyModel):
    class Meta:
        verbose_name = "class"
        verbose_name_plural = "classes"
        ordering = ["name"]
    name = models.CharField("Class name", max_length=64)
            
    def __unicode__(self):
        return self.name
    
    def is_same(self, another_class):
        return self.name == another_class.name
    
    def number_of_species(self):
        return TaxonomySpecies.objects.filter(taxonomy_family__taxonomy_order__taxonomy_class=self).count()


class TaxonomyOrder(ClickableTaxonomyModel):
    class Meta:
        verbose_name = "order"
        verbose_name_plural = "orders"
        ordering = ["name"]

    name = models.CharField("Order name", max_length=64)
    taxonomy_class = models.ForeignKey(TaxonomyClass, blank=True, null = True, related_name='taxonomy_orders')

    def __unicode__(self):
        return self.name
    
    def to_string(self):
        return "%s, %s" % (self.name, self.taxonomy_class.name if (self.taxonomy_class is not None) else "(No class assigned)" )

    def is_same(self, another_order):
        if self.name != another_order.name:
            return False
        if self.taxonomy_class is None and another_order.taxonomy_class is None:
            return True
        if self.taxonomy_class is None or another_order.taxonomy_class is None:
            return False
        return self.taxonomy_class.is_same(another_order.taxonomy_class)

    def number_of_species(self):
        return TaxonomySpecies.objects.filter(taxonomy_family__taxonomy_order=self).count()

    @transaction.atomic
    def save(self, *args, **kwargs):
        # if we have a class, it is possible that it does not exist in the database
        if self.taxonomy_class:
            if self.taxonomy_class.pk is None: #new entry, we need to save it
                # strangely if not using a temp variable, self.taxonomy_class doesn't get updated with the new pk... hm! didn't know that...
                temp = self.taxonomy_class
                temp.save()
                self.taxonomy_class = temp
        super(TaxonomyOrder, self).save(*args, **kwargs)


class TaxonomyFamily(ClickableTaxonomyModel):
    class Meta:
        verbose_name = "family"
        verbose_name_plural = "families"
        ordering = ["name"]
    name = models.CharField("Family name", max_length=64)
    taxonomy_order = models.ForeignKey(TaxonomyOrder, blank=True, null = True, related_name='taxonomy_families')

    def __unicode__(self):
        return self.name

    def to_string(self):
        return "%s, %s" % (self.name, self.taxonomy_order.to_string() if (self.taxonomy_order is not None) else "(No order, class assigned)" )

    def is_same(self, another_family):
        if self.name != another_family.name:
            return False
        if self.taxonomy_order is None and another_family.taxonomy_order is None:
            return True
        if self.taxonomy_order is None or another_family.taxonomy_order is None:
            return False
        return self.taxonomy_order.is_same(another_family.taxonomy_order)

    def number_of_species(self):
        return TaxonomySpecies.objects.filter(taxonomy_family=self).count()

    @transaction.atomic
    def save(self, *args, **kwargs):
        # if we have an order, it is possible that it does not exist in the database
        if self.taxonomy_order:
            if self.taxonomy_order.pk is None: #new entry, we need to save it
                # strangely if not using a temp variable, self.taxonomy_order doesn't get updated with the new pk... hm! didn't know that...
                temp = self.taxonomy_order
                temp.save()
                self.taxonomy_order = temp
        super(TaxonomyFamily, self).save(*args, **kwargs)


class TaxonomySpecies(models.Model):
    
    # Consider changing this class completely - flatting it out so that each species contains all the information about taxonomy
    # Advantages: 
    #    System is much easier to extend if later on we decide to display another taxon (say "subfamily"), otherwise a lot of changes are required to change the logic
    #    Query for species is faster - only one table
    # Disadvantages: 
    #    Will take more space in the DB (instead of a tree will keep no_taxon_fields * no_species)
    #    Saving will require a consistency check
    #    Changing taxonomy will be more complicated - due to consistency restrictions, if there are multiple entries with order - will have to have a special save which overrides all the inconsistent entries
    #        OR skip consistency check on save altogether and instead make a script that checks for that. 
    #    Contrary to now, consistency checks on import will have to check the entire DB
    
    class Meta:
        verbose_name = "species"
        verbose_name_plural = "species"
        ordering = ["name"]
    name = models.CharField("Scientific name", max_length=64)
    common_name = models.CharField(max_length=64)
    taxonomy_family = models.ForeignKey(TaxonomyFamily, blank=True, null = True, related_name='taxonomy_species')
    lifespan = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, help_text = "Field for lifespan data from AnAge")
    hagr_id = models.IntegerField(max_length=7, blank=True, null=True, help_text = "Field for HAGR ID to link to AnAge pages")

    # this method does not create the family, order, class in the database
    # it also does not load them from the database unless the parameter load_from_database is true (for input checking it should be false)
    @staticmethod
    def create_new_species(species_name, family_name, order_name, class_name, common_name, load_from_database):
        
        species_name = species_name.strip() 
        if (species_name is None) or (species_name == ""):
            return None
        
        species = TaxonomySpecies(name=species_name, common_name = common_name.strip())            
        if load_from_database:
            try:
                species = TaxonomySpecies.objects.get(name=species_name)
            except TaxonomySpecies.DoesNotExist:
                pass
        
        
        family_name = family_name.strip() 
        if (family_name is None) or (family_name == ""):
            return species

        species.taxonomy_family = TaxonomyFamily(name=family_name)
        if load_from_database:
            try:
                species.taxonomy_family = TaxonomyFamily.objects.get(name=family_name)
            except TaxonomyFamily.DoesNotExist:
                pass


        order_name = order_name.strip() 
        if (order_name is None) or (order_name == ""):
            return species

        species.taxonomy_family.taxonomy_order = TaxonomyOrder(name=order_name)
        if load_from_database:
            try:
                species.taxonomy_family.taxonomy_order = TaxonomyOrder.objects.get(name=order_name)
            except TaxonomyOrder.DoesNotExist:
                pass


        class_name = class_name.strip() 
        if (class_name is None) or (class_name == ""):
            return species
        
        species.taxonomy_family.taxonomy_order.taxonomy_class = TaxonomyClass(name=class_name)
        if load_from_database:
            try:
                species.taxonomy_family.taxonomy_order.taxonomy_class = TaxonomyClass.objects.get(name=class_name)
            except TaxonomyClass.DoesNotExist:
                pass

        return species

    @transaction.atomic
    def save(self, *args, **kwargs):
        # if we have a family, it is possible that it does not exist in the database

        if self.taxonomy_family:
            if self.taxonomy_family.pk is None: #new entry, we need to save it
                # strangely if not using a temp variable, self.taxonomy_family doesn't get updated with the new pk... hm! didn't know that...
                temp = self.taxonomy_family
                temp.save()
                self.taxonomy_family = temp
                
        super(TaxonomySpecies, self).save(*args, **kwargs)
        
    def validate(self):
        #cases: 
        try:
            species = TaxonomySpecies.objects.get(name=self.name)
            # have species; cases 1 & 2
            if (species.is_same(self)):
                # case 1. species already exists and we have the same parents
                return (1, "Species already in the database. Data is consistent. No action required.")
            else:
                # case 2. species already exists but parent chain is different
                return (2, "Already in DB as [%s]. Please review family/order/class inconsistencies. " % species.to_string())
            
        except TaxonomySpecies.DoesNotExist:
            # species is new; cases 3, 4 & 5
            # case 3. species is new, no family > no potential clashes
            if self.taxonomy_family is None:
                return (3, "Species is new and family is unassigned. Please review and upload again if necessary. If no action taken, entry will be uploaded without family/order/class info.")
            
            try:
                t_family = TaxonomyFamily.objects.get(name=self.taxonomy_family.name)
                # case 4. species is new, no clashes
                if t_family.is_same(self.taxonomy_family):
                    return (4, "New species to be added to the database. Data is consistent. No action required.")
     
                # case 5. species is new, but families/orders have wrong parents
                return (5, "Species is new, however the assigned family is inconsistent with existing records (in DB family has different order/class: [%s])." % t_family.to_string())

            except TaxonomyFamily.DoesNotExist:
                # species and family are new; cases 3, 4 & 5 (again - checking order)
                if self.taxonomy_family.taxonomy_order is None:
                    return (3, "Species and family are new while order is unassigned. Please review and upload again if necessary. If no action taken, entry will be uploaded without order/class info.")
                try:
                    t_order = TaxonomyOrder.objects.get(name=self.taxonomy_family.taxonomy_order.name)
                    if t_order.is_same(self.taxonomy_family.taxonomy_order):
                        # Species/family are new. Assigned order>class consistent with the database's structure. No action required. Entry will be uploaded.
                        return (4, "New species to be added to the database. Data is consistent. No action required.")
                    #New species. Assigned family>order>class inconsistent (!!!) with already existing records in the database. Please review! Entry will not be uploaded.
                    return (5, "Species and family are new, however the assigned order is inconsistent with existing records (in DB order has different class: [%s])." % t_order.to_string())
                except TaxonomyOrder.DoesNotExist:
                    # species, family and order are new; cases 3, 4 & 5 (again - checking class)
                    if self.taxonomy_family.taxonomy_order.taxonomy_class is None:
                        return (3, "Species, family, order are new, while class is unassigned. Please review and upload again if necessary. If no action taken, entry will be uploaded without class info.")
                    try:
                        TaxonomyClass.objects.get(name=self.taxonomy_family.taxonomy_order.taxonomy_class.name)
                        # No need to call "is_same" as it will check only the names 
                        return (4, "New species to be added to the database. Data is consistent. No action required.")
                    
                        #if t_class.is_same(self.taxonomy_family.taxonomy_order.taxonomy_class):
                        #    return (4, "New species to be added to the database. Data is consistent. No action required.")
                        #return (5, "Species, family and order are new, however the assigned class is inconsistent with existing records (in DB order has different class: %s)." % t_order.to_string())
                    
                    except TaxonomyClass.DoesNotExist:
                        # species, family, order and class are all new;
                        return (4, "New species to be added to the database. Data is consistent. No action required.")
                    

    def __unicode__(self):
        return self.name

    def to_string(self):
        return "%s%s, %s" % (self.name, (" (%s)" % self.common_name) if self.common_name is not "" else "", self.taxonomy_family.to_string() if (self.taxonomy_family is not None) else "(No family, order, class assigned)" )

    def short_description(self):
        family_name = order_name = class_name = ""
        if self.taxonomy_family:
            family_name = self.taxonomy_family.name
            if self.taxonomy_family.taxonomy_order:
                order_name = self.taxonomy_family.taxonomy_order.name
                if self.taxonomy_family.taxonomy_order.taxonomy_class:
                    class_name = self.taxonomy_family.taxonomy_order.taxonomy_class.name
        return "[%s]%s - [%s] - [%s] - [%s]%s" % (self.name, (" (%s)" % self.common_name) if self.common_name is not "" else "", family_name, order_name, class_name, (" (LS:%s)" % self.lifespan) if self.lifespan else "")


    def is_same(self, another_species):
        if self.name != another_species.name or self.common_name != another_species.common_name:
            return False
        if self.taxonomy_family is None and another_species.taxonomy_family is None:
            return True
        if self.taxonomy_family is None or another_species.taxonomy_family is None:
            return False
        return self.taxonomy_family.is_same(another_species.taxonomy_family)
