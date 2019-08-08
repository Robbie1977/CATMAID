from django.db import migrations


forward = """
    CREATE OR REPLACE FUNCTION refresh_skeleton_summary_table_selectively(skeleton_ids bigint[]) RETURNS void
    LANGUAGE plpgsql AS
    $$
    BEGIN
        -- Cable length, nodes, creation info, edition info
        WITH filtered_treenode AS (
            SELECT *
            FROM treenode
            JOIN UNNEST(skeleton_ids) query(query_skeleton_id)
                ON query.query_skeleton_id = treenode.skeleton_id
        ), node_data AS (
            SELECT creation.skeleton_id, creation.project_id,
                creation.user_id, creation.creation_time, edit.editor_id,
                edit.edition_time, counter.nodes, len.cable_length
            FROM
            (
              SELECT *, row_number() OVER(PARTITION BY skeleton_id ORDER BY edition_time DESC) AS rn
              FROM filtered_treenode
            ) edit
            JOIN
            (
              SELECT *, row_number() OVER(PARTITION BY skeleton_id ORDER BY creation_time ASC) AS rn
              FROM filtered_treenode
            ) creation
            ON edit.skeleton_id = creation.skeleton_id
            JOIN
            (
              SELECT skeleton_id, COUNT(*) AS nodes FROM filtered_treenode GROUP BY skeleton_id
            ) counter
            ON creation.skeleton_id = counter.skeleton_id
            JOIN
            (
              SELECT t1.skeleton_id, SUM(
                ST_3DLength(ST_MakeLine(ARRAY[
                    ST_MakePoint(t1.location_x, t1.location_y, t1.location_z),
                    ST_MakePoint(t2.location_x, t2.location_y, t2.location_z)
                ]::geometry[]))
              ) AS cable_length
              FROM filtered_treenode t1
              JOIN filtered_treenode t2
              ON t1.parent_id = t2.id
              GROUP BY t1.skeleton_id
            ) len
            ON creation.skeleton_id = len.skeleton_id
            WHERE edit.rn = 1 AND creation.rn = 1
        )
        INSERT INTO catmaid_skeleton_summary (skeleton_id,
            project_id, last_summary_update, original_creation_time,
            last_edition_time, last_editor_id, num_nodes, cable_length)
        (
            SELECT d.skeleton_id, d.project_id, now(), d.creation_time,
                d.edition_time, d.editor_id, d.nodes, d.cable_length
            FROM node_data d
        )
        ON CONFLICT (skeleton_id) DO UPDATE
        SET num_nodes = EXCLUDED.num_nodes,
            last_summary_update = EXCLUDED.last_summary_update,
            last_edition_time = EXCLUDED.last_edition_time,
            last_editor_id = EXCLUDED.last_editor_id,
            cable_length = EXCLUDED.cable_length;

    END;
    $$;
"""

backward = """
    CREATE OR REPLACE FUNCTION refresh_skeleton_summary_table_selectively(skeleton_ids bigint[]) RETURNS void
    LANGUAGE plpgsql AS
    $$
    BEGIN
        -- Cable length, nodes, creation info, edition info
        WITH filtered_treenode AS (
            SELECT *
            FROM treenode
            JOIN UNNEST(skeleton_ids) query(query_skeleton_id)
                ON query.query_skeleton_id = treenode.skeleton_id
        ), node_data AS (
            SELECT creation.skeleton_id, creation.project_id,
                creation.user_id, creation.creation_time, edit.editor_id,
                edit.edition_time, counter.nodes, len.cable_length
            FROM
            (
              SELECT *, row_number() OVER(PARTITION BY skeleton_id ORDER BY edition_time DESC) AS rn
              FROM filtered_treenode
            ) edit
            JOIN
            (
              SELECT *, row_number() OVER(PARTITION BY skeleton_id ORDER BY creation_time ASC) AS rn
              FROM filtered_treenode
            ) creation
            ON edit.skeleton_id = creation.skeleton_id
            JOIN
            (
              SELECT skeleton_id, COUNT(*) AS nodes FROM filtered_treenode GROUP BY skeleton_id
            ) counter
            ON creation.skeleton_id = counter.skeleton_id
            JOIN
            (
              SELECT t1.skeleton_id, SUM(
                ST_3DLength(ST_MakeLine(ARRAY[
                    ST_MakePoint(t1.location_x, t1.location_y, t1.location_z),
                    ST_MakePoint(t2.location_x, t2.location_y, t2.location_z)
                ]::geometry[]))
              ) AS cable_length
              FROM filtered_treenode t1
              JOIN filtered_treenode t2
              ON t1.parent_id = t2.id
              GROUP BY t1.skeleton_id
            ) len
            ON creation.skeleton_id = len.skeleton_id
            WHERE edit.rn = 1 AND creation.rn = 1
        )
        INSERT INTO catmaid_skeleton_summary (skeleton_id,
            project_id, last_summary_update, original_creation_time,
            last_edition_time, last_editor_id, num_nodes, cable_length)
        (
            SELECT d.skeleton_id, d.project_id, now(), d.creation_time,
                d.edition_time, d.editor_id, d.nodes, d.cable_length
            FROM node_data d
        );
    END;
    $$;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('catmaid', '0075_add_transaction_info_exec_time_index'),
    ]

    operations = [
            migrations.RunSQL(forward, backward)
    ]
