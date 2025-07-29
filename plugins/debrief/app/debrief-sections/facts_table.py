from reportlab.lib.units import inch0
from reportlab.platypus import Paragraph
from reportlab.platypus.flowables import KeepTogetherSplitAtTop

from plugins.debrief.app.utility.base_report_section import BaseReportSection

TABLE_CHAR_LIMIT = 1050


class DebriefReportSection(BaseReportSection):
    def __init__(self):
        super().__init__()
        self.id = 'facts-table'
        self.display_name = 'Operation Facts Table'
        self.section_title = 'FACTS FOUND IN OPERATION <font name=Courier-Bold size=17>%s</font>'
        self.description = 'The table below displays the facts found in the operation, the command run and the agent ' \
                           'that found the fact. Every fact, by default, gets a score of 1. If a host.user.password ' \
                           'fact is important or has a high chance of success if used, you may assign it a score of ' \
                           '5. When an ability uses a fact to fill in a variable, it will use those with the highest ' \
                           'scores first. A fact with a score of 0, is blacklisted - meaning it cannot be used in ' \
                           'an operation.'

    async def generate_section_elements(self, styles, **kwargs):
        flowable_list = []
        if 'operations' in kwargs:
            operations = kwargs.get('operations', [])
            for o in operations:
                flowable_list.append(
                    KeepTogetherSplitAtTop([
                        Paragraph(self.section_title % o.name.upper(), styles['Heading2']),
                        Paragraph(self.description, styles['Normal'])
                    ])
                )
                flowable_list.append(await self._generate_facts_table(o))
        return flowable_list

    async def _generate_facts_table(self, operation):
        fact_data = [['Trait', 'Value', 'Score', 'Source', 'Command Run']]
        exceeds_cell_msg = '... <font color="maroon"><i>(Value exceeds table cell character limit)</i></font>'
        facts = await operation.all_facts()
        for f in facts:
            if f.collected_by:
                paw_links = []
                for paw in f.collected_by:
                    paw_links.append('<link href="#agent-{0}" color="blue">{0}</link>'.format(paw))
                paw_value = ', '.join(paw_links)
                commands = set([lnk.decode_bytes(lnk.command) for lnk in operation.chain if lnk.id in f.links])
                command_value = '<br />'.join(commands)
            else:
                paw_value = f'{f.source[:3] + ".." + f.source[-3:]}'
                command_value = f'No Command ({f.origin_type.name})'
            fact_data.append([  
            self._truncate_for_cell(f.trait, max_chars=200, max_lines=3),  # Trait column is narrower  
            self._truncate_for_cell(f.value, max_chars=800, max_lines=15), # Value column gets more space  
            str(f.score),  
            paw_value,  # Keep paw_value as is since it's controlled  
            self._truncate_for_cell(command_value, max_chars=600, max_lines=10)  # Also truncate commands  
        ])

        return self.generate_table(fact_data, [1 * inch, 2.1 * inch, .6 * inch, .6 * inch, 2.1 * inch])

    def _truncate_for_cell(self, text, max_chars=800, max_lines=10):  
        """Truncate text to fit within table cell constraints"""  
        if not text:  
            return text  
            
        # Convert to string if not already  
        text = str(text)  
        
        # First check line count  
        lines = text.split('\n')  
        if len(lines) > max_lines:  
            # Too many lines, truncate by lines first  
            truncated_lines = lines[:max_lines-1]  
            truncated_lines.append('... <font color="maroon"><i>(Content truncated - too many lines)</i></font>')  
            text = '\n'.join(truncated_lines)  
        
        # Then check character count  
        if len(text) > max_chars:  
            # Find a good break point (try to break at word boundary)  
            truncate_point = max_chars - 100  # Leave room for truncation message  
            
            # Try to find last space before truncate point  
            last_space = text.rfind(' ', 0, truncate_point)  
            if last_space > truncate_point - 50:  # If space is reasonably close  
                truncate_point = last_space  
            
            text = text[:truncate_point] + '... <font color="maroon"><i>(Content truncated - too long)</i></font>'  
        
        return text