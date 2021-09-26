# simplex_algorithm
This repository contains an implementation of the simplex algorithm for the BloGPV-Project


getHouseholdData.py
Enthält Funktionen, welche Listen der
aktiven Consumer- und Producer-Haushalte,
sowie Python-Dictionarys mit aktuellen
Produktions- und Nachfragewerten erstellen


currentlyActiveCostDict.py
Erstellt ein Kosten-Dictionary für alle im
jeweiligen Intervall aktiven Haushaltepaare
und bringt dieses in die notwendige Form


constraintMatrix.py
Enthält Funktionen, welche die erforderlichen
Nebenbedingungen des linearen
Programms erstellen.


orderedDemandSupplyValues.py
Gewährleistet, dass die Reihenfolge
der Restriktionen des linearen Programms
der des Kostenvektors entspricht.


revisedSimplex.py
Führt den
revidierten Simplex-Algorithmus durch
Enthält Funktionen, welche die erforderlichen
Nebenbedingungen des linearen
Programms erstellen.
1. Erstellt eine Zielfunktion
2. Analysiert welcher Fall vorliegt
3. Erstellt einen Nebenbedindungsvektor b
unter Gewährleistung von proportionaler
Fairness
4. Führt den revisedSimplex Algorithmus aus
