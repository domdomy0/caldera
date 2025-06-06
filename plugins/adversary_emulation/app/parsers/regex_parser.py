import re
import sys 
import traceback 

from app.objects.secondclass.c_fact import Fact
from app.objects.secondclass.c_relationship import Relationship
from app.utility.base_parser import BaseParser

# Basic fallback logger (keep for error logging)
class PrintLogger:
    def debug(self, msg): 
        # print(f"PRINT_LOGGER_DEBUG: {msg}") # Commented out
        # sys.stdout.flush()
        pass # No-op for debug in cleaned version
    def info(self, msg): 
        # print(f"PRINT_LOGGER_INFO: {msg}") # Commented out
        # sys.stdout.flush()
        pass # No-op for info
    def warning(self, msg): 
        print(f"PRINT_LOGGER_WARNING: {msg}")
        sys.stdout.flush()
    def error(self, msg, exc_info=False): 
        print(f"PRINT_LOGGER_ERROR: {msg}")
        if exc_info:
            if isinstance(exc_info, BaseException): 
                traceback.print_exception(type(exc_info), exc_info, exc_info.__traceback__, file=sys.stderr)
            else:
                traceback.print_exception(*sys.exc_info(), file=sys.stderr)
        sys.stderr.flush()

class Parser(BaseParser):
    # This list might still be useful for the fallback search if direct injection fails.
    HOSTNAME_TRAITS_TO_SEARCH = ["host.hostname", "host.name.primary", "host.name"] 

    def __init__(self, parser_info):
        self.log = PrintLogger() # Initialize logger instance
        # self.log.debug(f"MyCustomRegexParser __init__ called. Parser instance: {id(self)}") # Cleaned
        
        try:
            super().__init__(parser_info) 
        except Exception as e_super_init:
            self.log.error(f"__init__ - super().__init__() FAILED: {e_super_init}", exc_info=True)
            # Depending on severity, might want to raise e_super_init or handle
        
        self.agent_hostname_from_link = None 
        try:
            if isinstance(parser_info, dict):
                self.agent_hostname_from_link = parser_info.get('agent_hostname') 
                if not self.agent_hostname_from_link:
                    self.log.warning("__init__ - 'agent_hostname' key NOT found in parser_info. " +
                                     "Ensure c_link.py is modified if direct hostname injection is expected.")
            else:
                self.log.warning(f"__init__ - parser_info is NOT a dict. Type: {type(parser_info)}")
        except Exception as e_info_proc:
            self.log.error(f"__init__ - Error processing parser_info for agent_hostname: {e_info_proc}", exc_info=True)
        
        self.link = None # Not typically set if apply() isn't the entry point

    def _find_hostname_fact_value(self, fact_list, list_name: str) -> str | None:
        """Helper to find hostname in a list of facts (fallback)."""
        if not self.log: self.log = PrintLogger()

        if fact_list and isinstance(fact_list, list):
            for fact_obj in fact_list:
                if isinstance(fact_obj, Fact):
                    if fact_obj.trait in self.HOSTNAME_TRAITS_TO_SEARCH:
                        return str(fact_obj.value) 
        return None

    def parse(self, blob: str) -> list[Relationship]:
        if not self.log: 
            print("EMERGENCY_LOGGER_PARSE: self.log was not set from __init__! Emergency PrintLogger created.")
            sys.stdout.flush()
            self.log = PrintLogger()

        relationships_to_return = []
        parser_configs = getattr(self, 'mappers', [])
        
        if not isinstance(parser_configs, list):
            self.log.error(f"parse() - self.mappers is not a list! Type: {type(parser_configs)}. Defaulting to empty list.")
            parser_configs = []

        if not parser_configs:
            self.log.warning("parse() - No parser_configs (mappers) available. Cannot parse.")
            return relationships_to_return

        source_node_fact = None
        preferred_source_trait = "host.hostname" 

        if hasattr(self, 'agent_hostname_from_link') and self.agent_hostname_from_link:
            source_node_fact = Fact(trait=preferred_source_trait, value=str(self.agent_hostname_from_link))
        else:
            self.log.warning("parse() - agent_hostname_from_link not available. Falling back to used_facts/source_facts search for hostname.")
            hostname_val_fallback = self._find_hostname_fact_value(getattr(self, 'used_facts', []), "used_facts")
            if not hostname_val_fallback:
                hostname_val_fallback = self._find_hostname_fact_value(getattr(self, 'source_facts', []), "source_facts")
            
            if hostname_val_fallback:
                source_node_fact = Fact(trait=preferred_source_trait, value=str(hostname_val_fallback))
            else:
                self.log.error("parse() - Could not determine Hostname via direct injection or fallback search. " +
                               "Host-linked relationships might be incomplete or use target as source.")

        for i, pc_config in enumerate(parser_configs):
            config_num = i + 1
            custom_parser_vals = getattr(pc_config, 'custom_parser_vals', None)
            edge_label_from_config = None
            fact_regex_pattern = None
            current_rule_source_trait = getattr(pc_config, 'source', 'N/A_TRAIT')

            if isinstance(custom_parser_vals, dict):
                edge_label_from_config = custom_parser_vals.get('edge_label')
                fact_regex_pattern = custom_parser_vals.get('regex')
                # Debug logs for edge_label finding are removed for cleanliness
            else:
                self.log.warning(f"parse() - Config #{config_num}: custom_parser_vals is NOT a dict or is None for trait '{current_rule_source_trait}'.")

            if not fact_regex_pattern: 
                self.log.warning(f"parse() - Config #{config_num}: SKIPPING - 'regex' not found for trait '{current_rule_source_trait}'.")
                continue
            
            if not current_rule_source_trait or current_rule_source_trait == 'N/A_TRAIT': 
                self.log.warning(f"parse() - Config #{config_num}: 'source' (trait for extracted fact) is MISSING. Skipping.")
                continue
            
            try:
                compiled_regex = re.compile(fact_regex_pattern)
            except re.error as e:
                self.log.error(f"parse() - Config #{config_num}: INVALID REGEX '{fact_regex_pattern}' for trait '{current_rule_source_trait}'. Error: {e}. Skipping.", exc_info=e)
                continue
            
            lines = blob.splitlines()
            if not lines and blob: lines = [blob]

            for line_num, line in enumerate(lines):
                try:
                    match = compiled_regex.search(line)
                    if match and match.groups(): 
                        value = match.group(1).strip()
                        if not value: continue

                        extracted_fact = Fact(trait=current_rule_source_trait, value=value)

                        if edge_label_from_config:
                            if source_node_fact: 
                                new_relationship = Relationship(source=source_node_fact, edge=edge_label_from_config, target=extracted_fact)
                                relationships_to_return.append(new_relationship)
                            else:
                                # No common source_node_fact, but edge_label exists. Create degenerate for target.
                                self.log.warning(f"    Edge '{edge_label_from_config}' specified for ({extracted_fact.trait}:{extracted_fact.value}), but no common source_node_fact (e.g. Hostname). Creating Degenerate Relationship for target fact.")
                                relationships_to_return.append(Relationship(source=extracted_fact))
                        else:
                            # No edge_label, create degenerate for the extracted fact.
                            relationships_to_return.append(Relationship(source=extracted_fact))
                except Exception as e_line_proc:
                    self.log.error(f"parse() - ERROR processing line {line_num+1} (config #{config_num}, trait '{current_rule_source_trait}'). Error: {e_line_proc}", exc_info=True) 
            
        return relationships_to_return
