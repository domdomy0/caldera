import re
from app.objects.secondclass.c_fact import Fact
from app.objects.secondclass.c_relationship import Relationship # Import Relationship
from app.utility.base_parser import BaseParser

class Parser(BaseParser):
    def __init__(self, parser_info):
        super().__init__(parser_info)
        # self.mappers is a list of ParserConfig objects from the YML
        # Each ParserConfig (pc) has pc.source (the trait string)
        # and pc.custom_parser_vals (the dict with 'regex')
        print(f"DEBUG: ThesisKVParser - INSTANCE CREATED. Mappers: {self.mappers}")

    def parse(self, blob: str) -> list[Relationship]: # Ensure return type hint matches expectation
        relationships_to_return = []
        parser_configs = self.mappers # These are the ParserConfig objects from your YML

        if not parser_configs:
            print("DEBUG: ThesisKVParser - No parser_configs (mappers) found.")
            return relationships_to_return

        for i, pc in enumerate(parser_configs):
            # pc.source is the trait string, e.g., "host.hostname"
            # pc.custom_parser_vals is the dict like {'regex': 'Host Name:\s+(.+)'}
            if pc.custom_parser_vals and 'regex' in pc.custom_parser_vals:
                fact_regex_pattern = pc.custom_parser_vals.get('regex')
                print(f"DEBUG: ThesisKVParser - Config {i+1}: Using regex '{fact_regex_pattern}' for source trait '{pc.source}'")

                for line_num, line in enumerate(blob.splitlines()):
                    try:
                        match = re.search(fact_regex_pattern, line)
                        if match and match.groups(): # Ensure there's a capturing group
                            value = match.group(1).strip() # Get the first captured group
                            print(f"DEBUG: ThesisKVParser - Config {i+1}, Line {line_num+1}: MATCH! Extracted value: '{value}' for trait '{pc.source}'")
                            
                            # Create the Fact object
                            # The default score for a Fact is 1, which is fine.
                            new_fact = Fact(trait=pc.source, value=value) 
                            print(f"DEBUG: ThesisKVParser - Fact created. Trait: {new_fact.trait}, Value: {new_fact.value}, Score: {new_fact.score}")
                            
                            # Wrap the Fact in a degenerate Relationship object.
                            # Link.create_relationships expects a list of Relationship objects.
                            # The score of this "relationship" can be the score of the fact itself.
                            # Edge and Target are None as this parser only extracts standalone facts.
                            degenerate_relationship = Relationship(source=new_fact, 
                                                                   edge=None, 
                                                                   target=None, 
                                                                   score=new_fact.score) # Pass the fact's score
                            relationships_to_return.append(degenerate_relationship)
                            print(f"DEBUG: ThesisKVParser - Degenerate relationship created for fact. Source: {degenerate_relationship.source.trait}={degenerate_relationship.source.value}")
                    except Exception as e:
                        print(f"ERROR: ThesisKVParser - Config {i+1}, Line {line_num+1}: Exception parsing line: {e}")
            else:
                print(f"DEBUG: ThesisKVParser - Config {i+1}: Skipping, no custom_parser_vals with 'regex' for source trait '{pc.source}'")


        print(f"DEBUG: ThesisKVParser - PARSE METHOD COMPLETED. Returning {len(relationships_to_return)} wrapped 'relationships'.")
        return relationships_to_return
