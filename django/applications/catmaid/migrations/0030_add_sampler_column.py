# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2017-12-16 00:24

import django.core.validators
from django.db import migrations, models

forward_history = """
    SELECT disable_history_tracking_for_table('catmaid_sampler'::regclass,
            get_history_table_name('catmaid_sampler'::regclass));

    -- Update table columns, add inverval boundary column,
    -- add interval_error column
    ALTER TABLE catmaid_sampler
    ADD COLUMN create_interval_boundaries bool,
    ADD COLUMN interval_error double precision;

    UPDATE catmaid_sampler
    SET create_interval_boundaries = FALSE,
        interval_error = 0.0;

    ALTER TABLE catmaid_sampler
    ALTER COLUMN create_interval_boundaries SET NOT NULL,
    ALTER COLUMN interval_error SET NOT NULL;

    -- Update history table
    ALTER TABLE catmaid_sampler__history
    ADD COLUMN create_interval_boundaries bool,
    ADD COLUMN interval_error double precision;

    UPDATE catmaid_sampler__history
    SET create_interval_boundaries = FALSE,
        interval_error = 0.0;


    SELECT enable_history_tracking_for_table('catmaid_sampler'::regclass,
            get_history_table_name('catmaid_sampler'::regclass), FALSE);
"""

backward_history = """
    SELECT disable_history_tracking_for_table('catmaid_sampler'::regclass,
            get_history_table_name('catmaid_sampler'::regclass));

    ALTER TABLE catmaid_sampler
    DROP COLUMN create_interval_boundaries;
    ALTER TABLE catmaid_sampler__history
    DROP COLUMN create_interval_boundaries;

    ALTER TABLE catmaid_sampler
    DROP COLUMN interval_error;
    ALTER TABLE catmaid_sampler__history
    DROP COLUMN interval_error;

    SELECT enable_history_tracking_for_table('catmaid_sampler'::regclass,
            get_history_table_name('catmaid_sampler'::regclass), FALSE);
"""

class Migration(migrations.Migration):

    dependencies = [
        ('catmaid', '0029_fix_stack_class_instance_constraints'),
    ]

    operations = [
        migrations.RunSQL(
            forward_history,
            backward_history,
            [
                migrations.AddField(
                    model_name='sampler',
                    name='create_interval_boundaries',
                    field=models.BooleanField(default=True)),
                migrations.AddField(
                    model_name='sampler',
                    name='interval_error',
                    field=models.FloatField()),
            ],
        ),
    ]
