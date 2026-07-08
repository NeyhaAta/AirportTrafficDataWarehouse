## Project 8: Data Warehouse setup for Aviation Stack
## Business Requirements:
Analyze the air traffic patterns of the ISP, JFK and LGA
Functional Requirements:
Track cancelled flights by airlines,
More requirements will be given by the professor
Data Requirements:
Data (provided by the professor).
Reference data for airports.

## Problem Context
Air travel generates large amounts of data every day, including information about flights, airlines, airports, delays, and cancellations. Without a centralized system, it can be difficult to organize this data and identify meaningful trends. This project focuses on building a data warehouse using Aviation Stack data to analyze air traffic patterns at John F. Kennedy International Airport (JFK), LaGuardia Airport (LGA), and Long Island MacArthur Airport (ISP). The goal is to organize flight data into a structured database that supports reporting and business intelligence. By analyzing flight activity and cancellations, the project will help identify traffic trends, compare airport and airline performance, and provide interactive dashboards that support data-driven decision making.

## Requirements:

## Business Requirements
* Compare flight activity between the three airports.
* Identify peak travel periods by day, month, and season.
* Track the total number of flights for each airport.
* Monitor flight cancellations by airline and airport.
* Compare airline performance across the three airports.
* Identify trends in flight arrivals and departures over time.
* Measure airport traffic growth or decline throughout the year.
* Provide dashboards and reports for analyzing air traffic data.
* Support data-driven decision making for airport and airline operations.
* A map of the airports with the most traffic highlighted for month, airline, airplane
* Identify which airlines have the highest and lowest cancellation rates.
* Compare the number of arrivals and departures for each airport.
* Analyze flight activity by airline, airport, and airplane.
* Track cancelled flights over time by day, month, and year.
* Compare flight activity during weekdays and weekends.
* Identify the busiest airlines operating at each airport.
* Provide interactive filters by airport, airline, airplane, month, and year.
* Generate key performance indicators (KPIs) such as total flights, total cancellations, and cancellation rate.
* Identify changes in air traffic patterns over time.
* Centralize aviation data into a single data warehouse for reporting and analysis.
* Analyze flight patterns by season (Winter, Spring, Summer, and Fall).
* Analyze flight patterns by airline, month, and quarter.
* Display a map showing flight concentration based on the selected airline, month, or season.
* Provide charts showing the number of flights by airline.
* Provide charts showing the number of flights by month.
* Provide charts showing the number of flights by airport.


## Functional Requirements


* Create dashboards to visualize the data.
* Display a map of the airports with the most traffic highlighted by month, airline, and airplane.
* Allow users to filter the data by airport, airline, airplane, month, and year.
* Calculate total flights, total cancellations, and cancellation rates.
* Compare flight activity between JFK, LGA, and ISP.
* Support trend analysis for flight activity and cancellations over time.
* Categorize flight data into Winter, Spring, Summer, and Fall.
* Aggregate flight data by month and quarter.
* Aggregate flight data by airline and airport.
* Generate a map visualizing flight concentration.
* Allow users to filter the map by airline.
* Allow users to filter the map by month.
* Allow users to filter the map by season.
* Generate charts displaying the number of flights per airline.
* Generate charts displaying the number of flights per month.
* Generate charts displaying the number of flights per airport.
* Support interactive filtering across all dashboards and visualizations.

## Data Requirements

* Data Source: from AviationStack API, real time and historical flight, airline, and airport data.
* Entities: Star schema including central flight fact table and dimension tables for airport, airline, aircraft, and date
* Data Ingestion: API data is pulled and put into one file and ingested into a storage
* Data Cleaning: Remove null values, fix data types, and standardize field formats
* Data Quality: Ensure unique records and consistent IATA codes
* Storage Layers: utilize a medallion archiecture (Bronze: raw, Silver: cleaned, Gold: Curated) for organization

## Requirement Analysis
The data is sourced from an API on the website aviationstack the data provides real time flight status, historical flights, airline routes, airports, aircrafts.
We then need to ingest the different types of data into a storage.
Then we reformat the data into proper fields and data types.
Clean the data by removing null values and fixing data types.
Put the clean data into a separate storage.
Transform the clean data.
Load the data.
Consolidate all the different types of data.
Put all the data into the data warehouse.
Create fact and dimension tables in the data warehouse.
Create relationships between the different tables.
Store airport, airline, aircraft, and flight information.
Update the data warehouse when new data is received from the API.
Generate reports from the data warehouse.

## Key Questions
* Which airport (JFK, LGA, or ISP) has the highest volume of flights?
* Which airlines operate the most flights at each airport?
* Which airline has the highest number of cancelled flights?
* Which airport experiences the most flight cancellations?
* How do air traffic patterns change by day, month, and season?
* What are the busiest travel periods for each airport?
* Which days of the week have the highest flight activity?
* What is the cancellation rate for each airport?
* How does airline performance compare across JFK, LGA, and ISP?
* What trends can be identified in flight activity over time?



C. Architecture

### 1. Information Architecture
- Describe the structure and flow of the information.
- Include diagrams or images if necessary. 
  - ![Information Architecture Diagram](path_to_image)

The information architecture describes how flight information moves through the system. Flight data is collected from the Aviation Stack API, while supporting reference data such as airport, airline, aircraft, and geographic information is collected from reference datasets. The information is gathered, cleaned, transformed, and consolidated before being stored in the data warehouse. The processed data is then used to generate reports, interactive dashboards, maps, and visualizations that allow users to analyze air traffic patterns, flight activity, and airline performance at JFK, LGA, and ISP airports. Stakeholders such as airport managers, airline managers, and data analysts can use this information to support data-driven decision making.



### 2. Data Architecture
The data is sourced from AviationStack API and pulled (ingested) from it and put into the Raw Storage (Bronze layer).
It is pulled/ingested again from the Bronze layer, cleans the data and put into a clean data storage (Silver layer).
Then it is pulled again from the Silver layer, and put into a Curated Data (Gold layer) where all the data is curated for each user.
Lastly it is pulled from the Gold layer and put into the Data Warehouse and forms the BI Solution

#### Medallion Architecture (if applicable)
- If your solution uses a data lake or lakehouse (e.g., Delta Lake, Databricks, Microsoft Fabric, Snowflake), describe how data moves through the medallion layers. Omit this part if it does not apply to your architecture.
- Stages:
  - **Bronze**: Raw, unprocessed data ingested directly from source systems.
  - **Silver**: Cleaned, conformed, and enriched data.
  - **Gold**: Aggregated, business-ready data for analytics and reporting.
- Include a diagram if helpful.
  - ![Medallion Architecture Diagram](path_to_image)We 

### 3. Technical Architecture
- Define the software and hardware systems involved in the project.
- List any key technologies, tools, or platforms used. 
  - Example: 
    - Python for data analysis
    - Azure for cloud computing 

The technical architecture lists the software, platforms, and tools that implement each layer of the pipeline. All storage and warehouse components are cloud-hosted managed services, with pipeline code developed locally and deployed to run on a schedule. The proposed technology stack is summarized below.

Layer
Tool/Technology
Purpose
Data Source
AviationStack REST API
Provides flight status, historical flights, airline routes, airports, and aircraft data
Ingestion & Cleaning
Python (requests, pandas)
Pull API data, flatten JSON, remove nulls, fix data types
Orchestration
Scheduled jobs / Apache Airflow  
Automate and schedule pipeline runs so the warehouse stays current 
Storage / Data Lake
Cloud storage (Azure Data Lake or Amazon S3) 
Holds the Bronze (raw) and Silver (clean) layers
Data Warehouse
Snowflake / Azure Synapse / SQL Server
Hosts the gold layer star schema (Fact_Flights + dimensions)
Transformation Modeling
SQL / dbt
Builds the Silver and Gold models and table relationships
BI / Visualization
Power BI or Tableau
Dashboards, traffic map, KPIs, and interactive filters
Version Control
Git / Github
Manages pipelines and transformation code

Hardware. No dedicated on-premise hardware is required — ingestion, storage, the warehouse, and the BI service all run on cloud infrastructure, while a standard development machine is used to build and test the pipeline.

### 4. Product Architecture
- Provide an overview of the product's overall structure.
- Include any major components and how they interact.

The product is an end-to-end aviation data warehouse and business-intelligence solution. It is made up of six major components that pass data from one to the next:

Ingestion Service — a Python service that pulls data from the AviationStack API and writes it to the Bronze layer.
Data Lake — cloud storage that holds the raw (Bronze) and cleaned (Silver) data.
Transformation Layer — SQL/dbt logic that cleans Bronze into Silver and models Silver into the Gold star schema.
Data Warehouse — the Gold star schema (Fact_Flights plus dimensions) that acts as the central source of truth.
BI Layer — Power BI or Tableau dashboards delivering the traffic map, KPIs, and interactive filters.
End Users — airport and airline stakeholders who interact with the dashboards to answer the project's key questions.

How the components interact. Data flows in one direction: API → Ingestion → Bronze → Transformation → Silver → Curated Data (Gold) → Data Warehouse → BI → Users. On each scheduled run, new flight data from the API updates the Bronze layer and propagates downstream, so the dashboards always reflect the latest air-traffic activity.

## D. Modeling
Dimensional Modeling 
Explain the dimensional modeling
- Example:
  - **Facts**: describe all the facts
  - **Dimension**: include all dimensions

*Include any necessary images or diagrams to clarify the architecture.*
  - ![Dimensional Modeling Diagram](path_to_image)

<img width="499" height="317" alt="Screenshot 2026-07-06 at 2 44 41 PM" src="https://github.com/user-attachments/assets/304dcdef-4072-4ecb-af68-65a1e83bf7b7" />

## E. Methodology and Implementation

The project followed an Agile approach because the data warehouse was developed in multiple stages. The team worked through data collection, cleaning, modeling, visualization, and testing. This allowed each part of the project to be tested before moving to the next stage.

### Project Phases

#### Sprint 1: Setup and Data Collection
The first phase focused on setting up the GitHub repository, Azure storage, and the Python development environment. The raw flight data was transferred from the Google Cloud Storage source into the Azure Bronze storage layer.

#### Sprint 2: Data Processing and Cleaning
The raw flight data was processed using Python and pandas. Nested flight records were flattened into columns, incomplete records were handled, duplicate records were removed, and data types were standardized. The cleaned dataset was stored as `flights_cleaned.csv` in the Silver layer.

#### Sprint 3: Data Modeling
The cleaned flight data was organized into a dimensional model. A star schema was created with a central flight fact table and dimensions for airport, airline, aircraft, and date. This structure allows the data to be analyzed from different perspectives.

#### Sprint 4: Visualization and Testing
Python, pandas, and Matplotlib were used to create visualizations from the cleaned flight dataset. The results were tested by comparing calculated totals and KPIs with the source data. The visualization outputs were saved in the `visualizations` folder.

### Metadata Management

The project uses metadata to document the meaning, format, and source of the data used in the warehouse.

#### Main Fact Table

The `fact_flights` table stores flight-level information, including:

- Flight date
- Flight number
- Flight status
- Departure airport
- Arrival airport
- Airline
- Aircraft
- Departure delay
- Arrival delay
- Scheduled departure and arrival times
- Actual departure and arrival times

#### Dimension Tables

- `dim_airport`: Stores airport information such as IATA code, ICAO code, and airport name.
- `dim_airline`: Stores airline name, IATA code, and ICAO code.
- `dim_aircraft`: Stores aircraft registration and aircraft type information.
- `dim_date`: Stores date, year, month, month name, day of week, and weekend indicators.

### Source-to-Target Mapping

The original AviationStack data contains nested flight, airline, aircraft, departure, and arrival information. The data was flattened and mapped into the Silver dataset. The cleaned fields were then used to create the Gold fact and dimension tables.

Examples include:

- `flight_date` → `dim_date`
- `flight_status` → `fact_flights`
- `airline_name` → `dim_airline`
- `aircraft_registration` → `dim_aircraft`
- `dep_iata` → departure airport
- `arr_iata` → arrival airport
- `dep_delay` → departure delay measure

### Main Functions

The project uses Python functions and transformation steps to move and process data.

- `list_gcs_objects()` lists objects available in the source Google Cloud Storage bucket.
- `make_blob_name()` creates the destination path for files transferred to Azure.
- `transfer()` transfers source data into Azure Blob Storage.
- `build_container_client()` connects to the Azure storage container.
- `flatten_record()` converts nested flight records into a flat tabular format.

The visualization script reads the cleaned flight dataset, calculates KPIs, groups flight records by different categories, and generates charts.

### ETL and ELT

The project uses a combination of ETL and ELT.

**ELT (Extract, Load, Transform):** Raw flight data is extracted from the source and loaded into the Bronze layer before transformation. This preserves the original data.

**ETL (Extract, Transform, Load):** Data is extracted from Bronze, cleaned and transformed using Python, and loaded into the Silver layer. The cleaned data is then transformed into fact and dimension tables for the Gold layer.

### Tools Used

- Python
- pandas
- Matplotlib
- Google Cloud Storage
- Azure Blob Storage
- Google Colab
- Git
- GitHub
- Power BI


## F. Visualization

Python, pandas, and Matplotlib were used to analyze the cleaned flight dataset and generate visualizations. The charts were created by the `airport_visualizations.py` script and saved in the `visualizations` folder.

### Departures by Airport

This visualization compares total flight departures between JFK, LGA, and ISP.

<img width="1579" height="977" alt="01_departures_by_airport" src="https://github.com/user-attachments/assets/e9dad5b3-f109-4f70-af9c-82b03855ae16" />

### Cancellation Rate by Airport

This chart compares the percentage of cancelled flights at each airport.

<img width="1580" height="977" alt="02_cancellation_rate_by_airport" src="https://github.com/user-attachments/assets/06619d75-dec9-418a-941d-0a4b679a7b98" />

### Top Airlines by Departures

This chart identifies the airlines with the highest number of departures across the three-airport system.

<img width="1774" height="1178" alt="03_top_airlines_by_departures" src="https://github.com/user-attachments/assets/5b54485d-8eae-4d28-befe-12871b6320f8" />

### Departures by Month

This visualization shows changes in flight activity over time.

<img width="1979" height="978" alt="04_departures_by_month" src="https://github.com/user-attachments/assets/aa586390-dbda-425f-8b6b-d4d176f2ca7e" />

### Airlines with the Highest Cancellation Rates

This chart compares cancellation rates among airlines with a significant number of flights.

<img width="1781" height="1178" alt="05_highest_airline_cancellation_rates" src="https://github.com/user-attachments/assets/5abccdf1-299c-449b-b40f-f9a02c4ad160" />

### Departures by Season

This visualization compares flight activity during Winter, Spring, Summer, and Fall.

<img width="1579" height="976" alt="06_departures_by_season" src="https://github.com/user-attachments/assets/ad2857ef-1bda-4214-a654-14e1aab078c1" />

### Departures by Day of Week

This chart compares flight activity across the days of the week.

<img width="1779" height="978" alt="07_departures_by_day_of_week" src="https://github.com/user-attachments/assets/4b92066d-0597-41c3-b576-125d486d1609" />

### Average Departure Delay by Airport

This visualization compares average departure delays between JFK, LGA, and ISP.

<img width="1579" height="977" alt="08_average_departure_delay_by_airport" src="https://github.com/user-attachments/assets/099682bc-1c4a-444b-af2b-59f58421a36a" />

## G. Insights

The analysis of 987,728 flight records produced several important findings:

- JFK had the highest flight volume with 733,903 departures, representing approximately 74% of the flights in the dataset.
- LGA recorded 247,288 departures, while ISP recorded 6,537 departures.
- LGA had the highest cancellation rate, while ISP had the lowest cancellation rate.
- Delta had the highest overall departure volume across the three airports.
- Flight activity was relatively stable throughout the week, although Saturday had the lowest number of departures.
- Spring had the highest flight volume among the four seasons.
- Average departure delay was highest at JFK and lowest at ISP.
- High flight volume did not always result in a high cancellation rate. Some high-volume airlines maintained cancellation rates close to the overall average.

The project also identified data quality limitations. Arrival delay contained unrealistic outlier values, aircraft information was missing for many records, and some months had incomplete data coverage. Because of these limitations, departure delay was used as the primary measure for delay analysis.


## H. Conclusion

The project successfully developed an aviation data warehouse solution for analyzing flight activity at JFK, LGA, and ISP airports. Flight data was moved through Bronze, Silver, and Gold data layers and organized into a dimensional model for analysis and reporting.

The project also produced Python-based visualizations that answer important business questions related to airport traffic, airline activity, cancellations, seasonal patterns, and departure delays. The results show that JFK dominates total flight volume, LGA has the highest airport cancellation rate, and flight activity patterns differ across airports and airlines.

The results can help airport managers, airline managers, and data analysts better understand traffic patterns and compare operational performance. Future improvements could include automating the data pipeline, adding additional airport and aircraft reference data, improving arrival-delay data quality, and developing additional interactive Power BI dashboards.


## I. References

1. *AviationStack — Real-Time Flight Status & Global Aviation Data API*. APILayer, 2025.

2. *pandas: Python Data Analysis Library*. The pandas Development Team, 2025.

3. *Matplotlib: Visualization with Python*. The Matplotlib Development Team, 2025.

4. *Azure Blob Storage Documentation*. Microsoft, 2025.

5. *Google Cloud Storage Documentation*. Google, 2025.

6. *Power BI Documentation*. Microsoft, 2025.

7. Kimball, Ralph, and Margy Ross. *The Data Warehouse Toolkit: The Definitive Guide to Dimensional Modeling*. 3rd ed., Wiley, 2013.
