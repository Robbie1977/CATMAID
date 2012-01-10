#!/bin/sh

if [ $# -ne 3 ]
then
    echo "Usage: $0 <DATABASE-NAME> <DATABASE-USER> <DATABASE-PASWORD>"
    exit 1
fi

CATMAID_DATABASE="$1"
CATMAID_USER="$2"
CATMAID_PASSWORD="$(echo $3 | sed -e "s/\\\\/\\\\\\\/g" -e "s/'/\\\'/g")"

cat <<EOSQL
CREATE ROLE "$CATMAID_USER" LOGIN PASSWORD '$CATMAID_PASSWORD';

CREATE DATABASE "$CATMAID_DATABASE" OWNER "$CATMAID_USER";

\c $CATMAID_DATABASE

CREATE FUNCTION connectby(text, text, text, text, integer, text) RETURNS SETOF record
    LANGUAGE c STABLE STRICT
    AS '\$libdir/tablefunc', 'connectby_text';
CREATE FUNCTION connectby(text, text, text, text, integer) RETURNS SETOF record
    LANGUAGE c STABLE STRICT
    AS '\$libdir/tablefunc', 'connectby_text';
CREATE FUNCTION connectby(text, text, text, text, text, integer, text) RETURNS SETOF record
    LANGUAGE c STABLE STRICT
    AS '\$libdir/tablefunc', 'connectby_text_serial';
CREATE FUNCTION connectby(text, text, text, text, text, integer) RETURNS SETOF record
    LANGUAGE c STABLE STRICT
    AS '\$libdir/tablefunc', 'connectby_text_serial';

CREATE PROCEDURAL LANGUAGE plpgsql;
EOSQL
