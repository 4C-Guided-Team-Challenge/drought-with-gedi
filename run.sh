# for GEDI query
# psql query for L2B 
<<<<<<< HEAD
# python3 drought/data/gedi_query_psql_daily.py \
#         --start_time '2019-1-1' --end_time '2022-12-31' --time_delta 7 \
#         --product_level level_2b --fields pai 

python3 drought/data/gedi_query_psql_monthly.py \
        --year_range 2019 2023 --product_level level_2b \
        --fields pai rh100 beam_type sensitivity solar_elevation cover 


# python3 drought/data/gedi_query_psql_daily.py \
#         --start_time '2019-1-1' --end_time '2022-12-31' --time_delta 7 \
#         --product_level level_2b --fields pai rh100 pai_z pavd_z \
#         --save_path data/interim/gedi_shots_l2b_7d_all.csv
# python3 -m pdb query_h5.py
=======
# python3 -m pdb drought/data/gedi_query_psql.py \
#         --year_range 2019 2023 --product_level level_2b --fields pai rh100 pai_z pavd_z

# python3 -m pdb query_h5.py

# seasonality analysis
python3 -m pdb drought/data/seasonality.py
>>>>>>> ys_variability
