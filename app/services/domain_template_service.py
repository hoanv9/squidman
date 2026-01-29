from app.models.domain_template import DomainTemplate
from app.extensions import db
from app.utils import validate_allowed_domains
import json
import logging


class DomainTemplateService:
    """Service layer for Domain Template CRUD operations."""

    @staticmethod
    def get_all_templates():
        """Get all domain templates."""
        return DomainTemplate.query.order_by(DomainTemplate.name).all()

    @staticmethod
    def get_template_by_id(template_id):
        """Get a single template by ID."""
        return DomainTemplate.query.get(template_id)

    @staticmethod
    def add_template(data):
        """Add a new domain template."""
        try:
            name = data.get('name', '').strip()
            domains_text = data.get('domains', '').strip()
            description = data.get('description', '').strip()

            if not name:
                return False, "Template name is required."

            if not domains_text:
                return False, "At least one domain is required."

            # Check for duplicate name
            if DomainTemplate.query.filter_by(name=name).first():
                return False, f"Template '{name}' already exists."

            # Parse and validate domains using central utility
            try:
                validated_domains = validate_allowed_domains(domains_text)
                if not validated_domains:
                    return False, "At least one valid domain is required."
            except ValueError as e:
                return False, str(e)

            new_template = DomainTemplate(
                name=name,
                domains=json.dumps(validated_domains),
                description=description
            )
            db.session.add(new_template)
            db.session.commit()
            return True, f"Template '{name}' added successfully with {len(validated_domains)} domains."

        except Exception as e:
            db.session.rollback()
            logging.error(f"Error adding template: {e}")
            return False, f"Error adding template: {str(e)}"

    @staticmethod
    def update_template(template_id, data):
        """Update an existing domain template."""
        try:
            template = DomainTemplate.query.get(template_id)
            if not template:
                return False, "Template not found."

            name = data.get('name', '').strip()
            domains_text = data.get('domains', '').strip()
            description = data.get('description', '').strip()

            if not name:
                return False, "Template name is required."

            # Check for duplicate name (excluding current template)
            existing = DomainTemplate.query.filter_by(name=name).first()
            if existing and existing.id != template_id:
                return False, f"Template '{name}' already exists."

            # Parse and validate domains using central utility
            try:
                validated_domains = validate_allowed_domains(domains_text)
                if not validated_domains:
                    return False, "At least one valid domain is required."
            except ValueError as e:
                return False, str(e)

            template.name = name
            template.domains = json.dumps(validated_domains)
            template.description = description
            db.session.commit()
            return True, f"Template '{name}' updated successfully."

        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating template: {e}")
            return False, f"Error updating template: {str(e)}"

    @staticmethod
    def delete_template(template_id):
        """Delete a domain template."""
        try:
            template = DomainTemplate.query.get(template_id)
            if not template:
                return False, "Template not found."

            name = template.name
            db.session.delete(template)
            db.session.commit()
            return True, f"Template '{name}' deleted successfully."

        except Exception as e:
            db.session.rollback()
            logging.error(f"Error deleting template: {e}")
            return False, f"Error deleting template: {str(e)}"

    @staticmethod
    def get_all_as_dict():
        """
        Get all templates as dictionary format for API.
        Returns: {"GroupName": [".domain1.com", ".domain2.com"], ...}
        """
        templates = DomainTemplate.query.order_by(DomainTemplate.name).all()
        result = {}
        for t in templates:
            result[t.name] = t.get_domains_list()
        return result

    @staticmethod
    def import_from_json(json_data, overwrite=False):
        """
        Import templates from JSON data.
        Args:
            json_data: dict in format {"GroupName": [domains], ...}
            overwrite: if True, overwrite existing templates with same name
        Returns: (success_count, skip_count, error_messages)
        """
        success_count = 0
        skip_count = 0
        errors = []

        try:
            for name, domains in json_data.items():
                if not isinstance(domains, list):
                    errors.append(f"Invalid format for '{name}': domains must be a list")
                    continue

                existing = DomainTemplate.query.filter_by(name=name).first()
                
                if existing:
                    if overwrite:
                        existing.domains = json.dumps(domains)
                        success_count += 1
                    else:
                        skip_count += 1
                else:
                    new_template = DomainTemplate(
                        name=name,
                        domains=json.dumps(domains),
                        description="Imported template"
                    )
                    db.session.add(new_template)
                    success_count += 1

            db.session.commit()
            return success_count, skip_count, errors

        except Exception as e:
            db.session.rollback()
            logging.error(f"Error importing templates: {e}")
            return 0, 0, [str(e)]

    @staticmethod
    def export_to_json():
        """Export all templates to JSON format."""
        return DomainTemplateService.get_all_as_dict()
