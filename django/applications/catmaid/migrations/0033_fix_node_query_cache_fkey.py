# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-12 03:48
from __future__ import unicode_literals

from django.db import migrations


forward = """
    ALTER TABLE node_query_cache
    DROP CONSTRAINT node_query_cache_project_id_fkey,
    ADD CONSTRAINT node_query_cache_project_id_fkey
        FOREIGN KEY (project_id)
        REFERENCES project(id)
        ON DELETE CASCADE;
"""

backward = """
    ALTER TABLE node_query_cache
    DROP CONSTRAINT node_query_cache_project_id_fkey,
    ADD CONSTRAINT node_query_cache_project_id_fkey
        FOREIGN KEY (project_id)
        REFERENCES project(id);
"""

class Migration(migrations.Migration):
    """Update the node_query_cache project foreign key to support cascading
    deletes.
    """

    dependencies = [
        ('catmaid', '0032_add_simple_section_cache_table'),
    ]

    operations = [
        migrations.RunSQL(forward, backward)
    ]

