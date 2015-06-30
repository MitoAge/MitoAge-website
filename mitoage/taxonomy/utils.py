from abc import abstractmethod, ABCMeta
from decimal import Decimal, InvalidOperation
import re

from django.db.models import Q
from mitoage.analysis.models import MitoAgeEntry, BaseComposition, CodonUsage
from mitoage.taxonomy.models import TaxonomySpecies


def normalize_query(query_string, findterms=re.compile(r'"([^"]+)"|(\S+)').findall, normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces and grouping quoted words together.
        Example: >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']'''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)] 

def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.'''
    query = None # Query to search for every search term        
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query


def este_equal(a, b):
    if ((not a) and b==""):
        return True
    if ((not b) and a==""):
        return True
    return (a==b)

# creates another DictReader after stripping the spaces from the first header
# could be optimized if we manually read only the first line from the file instead of creating an initial DictReader 
# (not sure how ineeficient it is at the moment...)
def create_dict_advanced_parser(csvfile):
    import csv
    reader = csv.DictReader(csvfile, dialect=csv.excel)
    header = [ h.strip() for h in reader.fieldnames ]
    reader = csv.DictReader(csvfile, fieldnames=header)
    reader.next()
    return reader


class CSVParserNoteOrWarning():
    def __init__(self, entry, additional_message):
        self.entry = entry
        self.additional_message = additional_message

class CSVParserError():

    def __init__(self, line_number, line_description):
        self.line = line_number
        self.line_description = line_description
        self.clashes = []

    def set_clash(self, with_line, entry, clash_message):
        self.clashes.append( (with_line, clash_message) )
        

class GenericCSVParser():
    __metaclass__ = ABCMeta
        
    def __init__(self, csvreader, expected_fields, required_fields):
        self.csvreader = csvreader
        self.dictlist = list(csvreader)
        self.required_fields = required_fields
        
        self.mismatched_columns = False;
        if not set(expected_fields).issubset( set(self.csvreader.fieldnames) ):
            #need stripping to all values! not only header, right? not sure... seems to work (there is stripping somewhere else)
            self.mismatched_columns = True;
        else:
            for dict_item in self.dictlist:
                for key in dict_item:   # dict_item is a dictionary    
                    if dict_item[key] == None:
                        dict_item[key] = ""
        
    def get_dict_iterator(self):
        return iter(self.dictlist)
    
    @abstractmethod
    def short_line_description(self, entry):
        return "Please override this in any CSV parser extending this class"
    
    @abstractmethod
    def validate_format(self, entry):
        # returns a message describing why the format is incorrect or "" if format is correct
        return "Please override this in any CSV parser extending this class"

    @abstractmethod
    def is_ignorable(self, entry):
        # returns a message describing why the format is incorrect or "" if format is correct
        return "Please override this in any CSV parser extending this class"

    @abstractmethod
    def inconsistent_entries(self, entry, another_entry):
        # returns a message describing the inconsistency or "" if there is none
        return "Please override this in any CSV parser extending this class"

    def validate_required_fields_and_formats(self):
        errors = []
        for i, entry in enumerate(self.dictlist):
            has_error = False
            is_null = False
            msg = ""
            for key in self.required_fields:
                if not entry[key] or entry[key].strip()=="":
                    is_null = True
                    has_error = True
                    break
            if is_null:
                msg = "%s - the following columns are required: %s; " % (self.short_line_description(entry), self.required_fields)
            
            message = self.validate_format(entry)
            if message!="":
                has_error = True
                msg += "%s - wrong format: %s" % (self.short_line_description(entry), message)
            if has_error:
                errors.append(CSVParserError(i+1, msg))
        return errors

    def find_duplicates(self):
        duplicates = []
        for i, entry in enumerate(self.dictlist):
            remaining_list = self.dictlist[i+1:]

            if entry in remaining_list:
                duplicates.append(CSVParserNoteOrWarning(entry, self.short_line_description(entry)))
        return duplicates
    
    def find_ignorables(self):
        ignore = []
        for entry in self.dictlist:
            message = self.is_ignorable(entry)
            if message!="":
                ignore.append(CSVParserNoteOrWarning(entry, "%s %s" % (self.short_line_description(entry), message) ))
        return ignore
    
    def validate_input_for_inconsistencies(self):
        errors = []
        for i, entry in enumerate(self.dictlist):
            remaining_list = self.dictlist[i+1:]

            error = None
            for j, future_entry in enumerate(remaining_list):
                
                additional_message = self.inconsistent_entries(entry, future_entry)
                if additional_message!="":                    
                    if error is None:
                        error = CSVParserError(i+1, self.short_line_description(entry))
                    error.set_clash(i+j+2, future_entry, "%s; %s" % (self.short_line_description(future_entry), additional_message))
                
            if error is not None:
                errors.append(error)
                    
        return errors

    def validate_all(self):
        errors = self.validate_required_fields_and_formats() + self.validate_input_for_inconsistencies()
        duplicates = self.find_duplicates()
        entries_to_ignore = self.find_ignorables()
        
        return (errors, duplicates, entries_to_ignore)


class TaxonomyParser(GenericCSVParser):
    
    def __init__(self, csvreader):
        super(TaxonomyParser, self).__init__(csvreader, ["Species","Family","Order","Class","Common name"], ["Species"])

    def short_line_description(self, entry):
        return "[%s]%s - [%s] - [%s] - [%s]" % (entry['Species'],("(%s)"%entry['Common name']) if entry['Common name'] else "",entry['Family'],entry['Order'],entry['Class'])

    def inconsistent_entries(self, entry, future_entry):
        # returns a message describing the inconsistency or "" if there is none
        additional_message = ""
        if (not este_equal(entry['Class'], future_entry['Class']) and este_equal(entry['Order'],future_entry['Order'])):
            additional_message +="<b>Class of [%s] can't be both [%s] and [%s]; </b>" % (entry['Order'], entry['Class'], future_entry['Class'])
        if (not este_equal(entry['Order'],future_entry['Order']) and este_equal(entry['Family'],future_entry['Family'])):
            additional_message +="<b>Order of [%s] can't be both [%s] and [%s]; </b>" % (entry['Family'], entry['Order'], future_entry['Order'])
        if (not este_equal(entry['Family'],future_entry['Family']) and este_equal(entry['Species'],future_entry['Species'])):
            additional_message +="<b>Family of [%s] can't be both [%s] and [%s]; </b>" % (entry['Species'], entry['Family'], future_entry['Family'])
        if (not este_equal(entry['Common name'], future_entry['Common name']) and este_equal(entry['Species'],future_entry['Species'])):
            additional_message +="<b>Common name of [%s] can't be both [%s] and [%s]; </b>" % (entry['Species'], entry['Common name'], future_entry['Common name'])
        return additional_message

    def validate_format(self, entry):
        return ""

    def is_ignorable(self, entry):
        # returns a message describing why the format is incorrect or "" if format is correct
        if ( not entry['Class'] or not entry['Order'] or not entry['Family']):
            species = TaxonomySpecies.create_new_species(entry['Species'], entry['Family'], entry['Order'], entry['Class'], entry['Common name'], False)
            # if species is "" or None, then automatically should be reported in errors, no need to include it here 
            if species:
                return "<b> >>> This is what will be saved in DB: [%s]</b>" % species.to_string()
        return ""

    def validate_against_database(self):
        # got through all the records and create a dictionary with newly created objects (but doesn't load them from database if exist - just fake objects to check consistency of input)
        # this also validates the new entries compared to existing entries in the database
        self.species = {}
        for row in self.get_dict_iterator():
            species = TaxonomySpecies.create_new_species(row['Species'], row['Family'], row['Order'], row['Class'], row['Common name'], False)
            if species is not None:
                self.species[row['Species']] = species
        
        # validate species, and based on the scores assign them to one of the dictionaries
        # 1, already: "Species already in the database - consistency for family, order and class. No action required. Entry will not be uploaded."
        # 2, err: "Species already in the database - inconsistencies (!!!) for family, order and/or class. Please review (at the moment update can be done only manually)! Entry will not be uploaded."
        # 3, incomplete: "New species without assigned family. Please review (!!!) and upload again if necessary. If no action taken, entry will be uploaded without family/order/class info."
        # 4, ok: "New species to be added. Assigned family>order>class consistent with the database's structure. No action required. Entry will be uploaded."
        # 5, err: "New species. Assigned family>order>class inconsistent (!!!) with already existing records in the database. Please review! Entry will not be uploaded."

        self.upload_validation_category = {1:[], 2:[], 3:[], 4:[], 5:[]}
        for sp in self.species.values():
            (validation_code, validation_text) = sp.validate()  # validation_text not really required...
            self.upload_validation_category[validation_code].append( (sp,validation_text) )

    # entries that are categorized as "already in the db" don't need to be reported as having missing fields (they are ignored but also not imported)
    def remove_warnings_for_already_in_db(self, ignored):
        new_ignored = []
        for item in ignored:
            item_species = TaxonomySpecies.create_new_species(item.entry['Species'], item.entry['Family'], item.entry['Order'], item.entry['Class'], item.entry['Common name'], False)

            not_found = True
            for entry in self.upload_validation_category[1]:
                if item_species.is_same(entry[0]):
                    not_found = False
                #new_ignored.append(CSVParserNoteOrWarning(item.entry, "Comparison of %s with %s = %s" % (item_species, entry[0], not_found)))
            if not_found:
                new_ignored.append(item)
        return new_ignored




class AnAgeParser(GenericCSVParser):

    def __init__(self, csvreader):
        super(AnAgeParser, self).__init__(csvreader, ["Species", "Lifespan", "HAGRID"], ["Species", "Lifespan", "HAGRID"])

    def short_line_description(self, entry):
        return "[%s] - [%s years] (HAGR ID:%s)" % (entry['Species'],entry['Lifespan'] if entry['Lifespan'] else "???", entry['HAGRID'] if (entry['HAGRID'] and entry['HAGRID'].strip()!="") else "???")

    def inconsistent_entries(self, entry, future_entry):
        # returns a message describing the inconsistency or "" if there is none
        additional_message = ""
        if entry['Species']==future_entry['Species'] and entry['Lifespan']!=future_entry['Lifespan']:
            additional_message +="<b>Lifespan of [%s] can't be both [%s] and [%s]; </b>" % (entry['Species'], entry['Lifespan'], future_entry['Lifespan'])
        if entry['Species']==future_entry['Species'] and entry['HAGRID']!=future_entry['HAGRID']:
            additional_message +="<b>HAGR ID of [%s] can't be both [%s] and [%s]; </b>" % (entry['Species'], entry['HAGRID'], future_entry['HAGRID'])
        return additional_message

    def validate_format(self, entry):
        message = ""

        try:
            Decimal(entry['Lifespan'])
        except InvalidOperation:
            message = "Lifespan must be a decimal number; "
            
        try:
            int(entry['HAGRID'])
        except ValueError:
            message += "HAGR ID must be an integer number; "

        return message

    def is_ignorable(self, entry):
        # returns a message describing why the format is incorrect or "" if format is correct
        return ""

    def validate_against_database(self):
        db_errors = []
        already_in_db = []
        consistent_changes = []
        
        for row in self.get_dict_iterator():
            try:
                species = TaxonomySpecies.objects.get(name=row['Species'])
                # assumes that row['Lifespan'] is a number (otherwise it would have been reported in the input consistency check
                try:
                    if Decimal(species.lifespan) == Decimal(row['Lifespan']) and int(species.hagr_id) == int(row['HAGRID']):
                        already_in_db.append(self.short_line_description(row))
                    else:
                        db_errors.append("Species %s already exists, however recorded lifespan or HAGR ID are different (DB: LS=%s, HAGR ID=%s; Input: LS=%s, HAGR ID=%s). " % (row['Species'],species.lifespan, species.hagr_id, row['Lifespan'], row['HAGRID']))
                except TypeError:
                    if species.lifespan == None and species.hagr_id == None:
                        if (self.short_line_description(row) not in consistent_changes):
                            consistent_changes.append( (row, self.short_line_description(row)) )
                    else:
                        db_errors.append("Species %s already exists, however recorded lifespan or HAGR ID are different (DB: LS=%s, HAGR ID=%s; Input: LS=%s, HAGR ID=%s). " % (row['Species'],species.lifespan, species.hagr_id, row['Lifespan'], row['HAGRID']))
            except TaxonomySpecies.DoesNotExist:
                db_errors.append("Species %s does not exist. Please create taxonomy first, before setting AnAge values. " % row['Species'])
        
        return (db_errors, already_in_db, consistent_changes)
        
        

class BaseCompositionParser(GenericCSVParser):

    def __init__(self, csvreader):
        super(BaseCompositionParser, self).__init__(csvreader, ["Species", "G", "C", "A", "T", "Other", "mtDNA size (bp)"], ["Species", "G", "C", "A", "T", "Other", "mtDNA size (bp)"])

    def short_line_description(self, entry):
        return "[%s - [G:%s;C:%s;A:%s;T:%s;O:%s] - size: %s bp]" % (entry['Species'],entry['G'],entry['C'],entry['A'],entry['T'],entry['Other'],entry['mtDNA size (bp)'])

    def inconsistent_entries(self, entry, future_entry):
        # returns a message describing the inconsistency or "" if there is none
        additional_message = ""
        if entry['Species']==future_entry['Species'] and entry['G']!=future_entry['G']:
            additional_message +="<b>G content of [%s] can't be both [%s] and [%s]; </b>" % (entry['Species'], entry['G'], future_entry['G'])
        if entry['Species']==future_entry['Species'] and entry['C']!=future_entry['C']:
            additional_message +="<b>C content of [%s] can't be both [%s] and [%s]; </b>" % (entry['Species'], entry['C'], future_entry['C'])
        if entry['Species']==future_entry['Species'] and entry['A']!=future_entry['A']:
            additional_message +="<b>A content of [%s] can't be both [%s] and [%s]; </b>" % (entry['Species'], entry['A'], future_entry['A'])
        if entry['Species']==future_entry['Species'] and entry['T']!=future_entry['T']:
            additional_message +="<b>T content of [%s] can't be both [%s] and [%s]; </b>" % (entry['Species'], entry['T'], future_entry['T'])
        if entry['Species']==future_entry['Species'] and entry['Other']!=future_entry['Other']:
            additional_message +="<b>Other content of [%s] can't be both [%s] and [%s]; </b>" % (entry['Species'], entry['Other'], future_entry['Other'])
        if entry['Species']==future_entry['Species'] and entry['mtDNA size (bp)']!=future_entry['mtDNA size (bp)']:
            additional_message +="<b>mtDNA size (bp) of [%s] can't be both [%s] and [%s]; </b>" % (entry['Species'], entry['mtDNA size (bp)'], future_entry['mtDNA size (bp)'])
        return additional_message

    def validate_format(self, entry):
        message = ""

        try:
            int(entry['G'])
            int(entry['C'])
            int(entry['A'])
            int(entry['T'])
            int(entry['Other'])
            int(entry['mtDNA size (bp)'])
        except ValueError:
            message += "G, C, A, T, Other, mtDNA size must all be integer numbers; "

        return message

    def is_ignorable(self, entry):
        # returns a message describing why the format is incorrect or "" if format is correct
        return ""

    def validate_against_database(self, section):
        db_errors = []
        already_in_db = []
        consistent_changes = []
        
        for row in self.get_dict_iterator():
            try:
                # get current species and get/create its associated mitoage entry
                current_species = TaxonomySpecies.objects.get(name=row['Species'])
                mitoage_entry, created = MitoAgeEntry.objects.get_or_create(species = current_species)
                
                # assumes that we have numbers (otherwise it would have been reported in the input consistency check) - shouldn't give error
                input_base_composition = BaseComposition(int(row['mtDNA size (bp)']), int(row['G']), int(row['C']), int(row['A']), int(row['T']), int(row['Other']))
                try:
                    base_composition = mitoage_entry.get_base_composition(section)
                    
                    if input_base_composition.is_same(base_composition):
                        already_in_db.append(self.short_line_description(row))
                    else:
                        db_errors.append("Species %s already exists, however base composition is different (DB: %s; Input: %s). " % (base_composition.to_string(), input_base_composition.to_string()))
                except TypeError:
                    if (self.short_line_description(row) not in consistent_changes):
                        consistent_changes.append( (row, self.short_line_description(row)) )

            except TaxonomySpecies.DoesNotExist:
                db_errors.append("Species %s does not exist. Please create taxonomy first, before setting Base composition values. " % row['Species'])
                
        
        return (db_errors, already_in_db, consistent_changes)

class CodonUsageParser(GenericCSVParser):

    @staticmethod
    def get_codon_usage_fields():
        return ["Species", "mtDNA size (bp)", "Amino Acids", "AUU", "AUC", "AUA", "CUU", "CUC", "CUA", "CUG", "UUA", "CAA", "CAG", "GUU", "GUC", "GUA", "GUG", "UUU", "UUC", "AUG", "UGU", "UGC", "GCU", "GCC", "GCA", "GCG", "GGU", "GGC", "GGA", "GGG", "CCU", "CCC", "CCA", "CCG", "ACU", "ACC", "ACA", "ACG", "UCU", "UCC", "UCA", "UCG", "AGU", "AGC", "UAU", "UAC", "UGG", "UUG", "AAU", "AAC", "CAU", "CAC", "GAA", "GAG", "GAU", "GAC", "AAA", "AAG", "CGU", "CGC", "CGA", "CGG", "AGA", "AGG", "STOP CODON - UAA", "STOP CODON - UAG", "STOP CODON - UGA"]

    def __init__(self, csvreader):
        super(CodonUsageParser, self).__init__(csvreader, CodonUsageParser.get_codon_usage_fields(), CodonUsageParser.get_codon_usage_fields()) 

    def short_line_description(self, entry):
        return "%s" % entry

    def inconsistent_entries(self, entry, future_entry):
        # returns a message describing the inconsistency or "" if there is none
        additional_message = ""
        
        for field_name in CodonUsageParser.get_codon_usage_fields():
            if field_name=="Species":
                continue
            if entry['Species']==future_entry['Species'] and entry[field_name]!=future_entry[field_name]:
                additional_message +="<b>%s of [%s] can't be both [%s] and [%s]; </b>" % (field_name, entry['Species'], entry[field_name], future_entry[field_name])
        return additional_message

    def validate_format(self, entry):
        message = ""

        try:
            for field_name in CodonUsageParser.get_codon_usage_fields():
                if field_name=="Species" or field_name=="Amino Acids":
                    continue
                int(entry[field_name])
        except ValueError:
            message += "All values other than species name must all be integer numbers; "

        return message

    def is_ignorable(self, entry):
        # returns a message describing why the format is incorrect or "" if format is correct
        return ""

    def validate_against_database(self, section):
        db_errors = []
        already_in_db = []
        consistent_changes = []
        
        for row in self.get_dict_iterator():
            try:
                # get current species and get/create its associated mitoage entry
                current_species = TaxonomySpecies.objects.get(name=row['Species'])
                mitoage_entry, created = MitoAgeEntry.objects.get_or_create(species = current_species)
                
                # assumes that we have numbers (otherwise it would have been reported in the input consistency check) - shouldn't give error
                input_codon_usage = CodonUsage()
                input_codon_usage.set_codon_usage_from_dictionary(row)
                input_codon_usage.aa = row['Amino Acids']
                input_codon_usage.size = row['mtDNA size (bp)']
                
                codon_usage = mitoage_entry.get_codon_usage(section)
                    
                if codon_usage == None:
                    if (self.short_line_description(row) not in consistent_changes):
                        consistent_changes.append( (row, self.short_line_description(row)) )
                elif input_codon_usage.same_values(codon_usage):
                    already_in_db.append(self.short_line_description(row))
                else:
                    db_errors.append("Species %s already exists, however codon usage is different (DB: %s; Input: %s). " % (codon_usage.to_string(), input_codon_usage.to_string()))

            except TaxonomySpecies.DoesNotExist:
                db_errors.append("Species %s does not exist. Please create taxonomy first, before setting codon usage values. " % row['Species'])
                
        
        return (db_errors, already_in_db, consistent_changes)
        