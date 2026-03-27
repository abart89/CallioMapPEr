# **Classes Taxonomy**

* bfo:continuant  
  * iao:information content entity  
    * oeo:energy system model  
      * CalliopeModel  
    * oeo:model component  
      * CalliopeTopologicalElement  
        * CalliopeNetworkNode  
        * CalliopeNetworkLink  
      * CalliopeTechnology  
        * CalliopeSupplyTechnology  
        * CalliopeDemandTechnology  
        * CalliopeStorageTechnology  
        * CalliopeTransmissionTechnology  
      * CalliopeEnergyCarrier  
    * iao:data item  
      * oeo:exogenous data  
        * oeo:program parameter  
      * oeo:endogenous data  
        * oeo:output data  
    * oeo:quantity value  
      * oeo:cost  
      * oeo:energy value  
      * oeo:emission value  
    * oeo:scenario  
    * oeo:data set  
      * oeo:time series  
        * oeo:typical period  
  * bfo:spatial region  
    * oeo:region of relevance  
  * bfo:temporal region  
    * oeo:time step  
      * oeo:scenario horizon  
* bfo:process (Occurrents)  
  * oeo:model calculation  
    * oeo:optimisation  
  * oeo:scenario projection  
* oeo:software framework  
  * "Calliope" (individual)

  # **Object Attributes Taxonomy**

* bfo:has part (and inverse bfo:part of)  
* iao:is about  
  * *(Note: oeo:quantity value of is specifically EXCLUDED for software variables to avoid the "reality trap")*  
* oeo:has information input  
* oeo:has information output  
* oeo:has quantity value  
* oeo:has unit  
* oeo:is based on

  # **Object Attributes Assignment**

| Attribute Name             | Domain                                | Range                   | Notes / Context                                                                         |
| :------------------------- | :------------------------------------ | :---------------------- | :-------------------------------------------------------------------------------------- |
| bfo:has part               | CalliopeModel                         | oeo:model component     | Links the model to its internal informational building blocks (Nodes, Techs, Links).    |
| bfo:part of                | oeo:optimisation                      | oeo:scenario projection | Contextualizes the solver run within the broader modeling exercise.                     |
| oeo:is based on            | oeo:scenario projection               | oeo:scenario            | Links the projection process to the narrative/informational scenario it tests.          |
| oeo:has information input  | oeo:optimisation                      | oeo:exogenous data      | Binds the compiled Footprint inputs (like parameters and limits) to the solver process. |
| oeo:has information output | oeo:optimisation                      | oeo:output data         | Binds the solved Footprint results (flows, costs) to the solver process.                |
| oeo:has quantity value     | oeo:exogenous data OR oeo:output data | oeo:quantity value      | Connects the data container to its semantic meaning (e.g., Cost, Energy).               |
| iao:is about               | CalliopeNetworkNode                   | oeo:region of relevance | Used ONLY if the node corresponds to a physical real-world location (e.g., Singapore).  |
| iao:is about               | oeo:output data OR oeo:exogenous data | oeo:time step           | Links a specific data point to the specific time it occurred (Single Timestep).         |
| iao:is about               | oeo:scenario                          | oeo:time step           | Links the entire narrative scenario to the total simulated horizon.                     |
| bfo:has part               | oeo:time series                       | oeo:output data         | Used for the Detailed Approach to group hourly output data into a single array.         |

  # **Data Attributes Assignment (Values & Strings)**

| Attribute Name           | Domain             | Range (Datatype) | Notes / Context                                                                                |
| :----------------------- | :----------------- | :--------------- | :--------------------------------------------------------------------------------------------- |
| oeo:has number           | oeo:quantity value | float / integer  | The actual mathematical magnitude (e.g., 50.0).                                                |
| oeo:has aggregation type | oeo:output data    | string           | e.g., "Sum", "Average". Used when linking a single data output to the entire scenario horizon. |
| has\_source\_repository  | oeo:scenario       | string (URI)     | Lightweight provenance replacing the need to model YAML files.                                 |

* 
