Intent: Add the ability for the skills to develop work within the source package. 
In other words, instead of the end-user creating a new package extension that
contains the new element (recipe step, or yardstick metric), the end-user plans
to send a PR to recipes or yardstick directly. Some considerations are:
- No longer internal functions should be avoided, but used when needed
- Documentation and testing should match the style of the existing code base
We will probably have to split the skill into 3:
- Main skill retains core approach
- Reference skill that deals with developing extensions (avoid internal functions)
- Reference skill that deals with developing within the source package (yardstick, recipes)

Phase 1 - Perform assesment of how much the skill would change. Hopefully most
reference skills will not need to change much since their content is very thematic, 
and the script references are relative. 
Phase 2 - Start planning the changes. For this, I would like to start with a
plan doc and a checklist. We should split into two phases, first update yardstick skill and
then the recipes one
