import json
import csv

def process_attribute(resource_name, attribute, parent_name=None):
    attribute_name = attribute.get('name', '')
    computed_optional_required = ''
    default_value = ''
    validators = []
    plan_modifiers = []
    array_of_rows = []

    primitive_type = False
    multi_elem_type = False
    nested_type = False
    # Check if attribute has a type
    attribute_type = ''
    if 'string' in attribute:
        attribute_type = 'string'
        primitive_type = True
    elif 'int64' in attribute:
        attribute_type = 'int64'
        primitive_type = True
    elif 'bool' in attribute:
        attribute_type = 'bool'
        primitive_type = True
    elif 'map_nested' in attribute:
        attribute_type = 'map_nested'
        nested_type = True
    elif 'single_nested' in attribute:
        attribute_type = 'single_nested'
    elif 'list' in attribute:
        attribute_type = 'list'
        multi_elem_type = True
    elif 'set' in attribute:
        attribute_type = 'set'
        multi_elem_type = True
    elif 'map' in attribute:
        attribute_type = 'map'
        multi_elem_type = True
    else:
        attribute_type = ''

    # Handle different attribute types
    computed_optional_required = attribute.get(attribute_type, {}).get('computed_optional_required', '')
    if primitive_type:
        # iterate over validators
        default_value = attribute[attribute_type].get('default', {}).get('static', '')
        for validator in attribute[attribute_type].get('validators', []):
            validators.append(validator.get('custom', {}).get('schema_definition', '.').split(".", 1)[1])
        # iterate over plan_modifiers
        for plan_modifier in attribute[attribute_type].get('plan_modifiers', []):
            plan_modifiers.append(plan_modifier.get('custom', {}).get('schema_definition', '.').split(".", 1)[1])
    elif attribute_type == 'single_nested':
        # Process nested attributes
        for nested_attibute in attribute.get('single_nested', {}).get('attributes', []):
            array_of_rows.extend(process_attribute(resource_name, nested_attibute, attribute_name))
    elif multi_elem_type:
        element_type = attribute[attribute_type].get('element_type', {})
        attribute_type = attribute_type + '_of_' + next(iter(element_type.keys()))
    elif nested_type:
        # Process nested attributes
        for nested_attibute in attribute.get(attribute_type, {}).get('nested_object', {}).get('attributes', []):
            array_of_rows.extend(process_attribute(resource_name, nested_attibute, attribute_name))

    # Join validators and plan_modifiers into comma-separated strings
    validators = ', '.join(validators)
    plan_modifiers = ', '.join(plan_modifiers)
    if parent_name:
        attribute_name = f'{parent_name}.{attribute_name}'
    row = [resource_name, attribute_name, attribute_type, computed_optional_required, default_value, validators, plan_modifiers]
    array_of_rows.append(row)
    return array_of_rows

# Read the provider_spec_schema.json file
with open('provider_code_spec.json', 'r') as file:
    data = json.load(file)

# Prepare the CSV file
with open('resource_attributes.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Resource Name', 'Attribute Name', 'attribute_type', 'computed_optional_required', 'default_value', 'validators', 'plan_modifiers'])

    # Iterate over each resource in the schema
    for resource in data.get('resources', []):
        resource_name = resource.get('name', '')
        for attribute in resource.get('schema', {}).get('attributes', []):
            rows = process_attribute(resource_name, attribute)
            writer.writerows(rows)

print("CSV file has been created successfully.")
