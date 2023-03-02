# for GEDI query
# psql query for L2B 
python3 drought/data/gedi_query_psql_daily.py \
        --start_time '2019-1-1' --end_time '2022-12-31' --time_delta 7 \
        --product_level level_2b --fields pai 

# python3 drought/data/gedi_query_psql_daily.py \
#         --start_time '2019-1-1' --end_time '2022-12-31' --time_delta 7 \
#         --product_level level_2b --fields pai rh100 pai_z pavd_z \
#         --save_path data/interim/gedi_shots_l2b_7d_all.csv
# python3 -m pdb query_h5.py