# for GEDI query
# psql query for L2B 
python3 -m pdb drought/data/gedi_query_psql.py \
        --year_range 2020 2023 --product_level level_2b --fields pai

# python3 -m pdb query_h5.py