# simplex algorithm
This repository contains an implementation of a simplex algorithm for p2p elcectricity trading


getHouseholdData.py
- contains functions that generates list of currently
  active households and python dictionarys for current
  supply and demand values of producer and consumer households

currentlyActiveCostDict.py
- builds a cost-dictionary for all currently active households
  and ensures the needed format


constraintMatrix.py
- contains functions that build the needed constraints for
  the linear programming problem

orderedDemandSupplyValues.py
-  ensures that the order of the constraints and the supply
   and the demand dictionaries is the same


simplex_main.py
-  runs the simplex algorithm
-  builds the objective function
-  analyses if demand > supply, demand < supply or demand = supply
-  builds righthandside constraints b
-  ensures proportional fairness

# needed files
- AssetListe.json
- tradingCost_prosumers_to_all_households_nested.json
- pairsAndReductions.json (this is only needed to analyze results. not the algorithm itself)

This algorithm accepts household data which is structured like the API data
