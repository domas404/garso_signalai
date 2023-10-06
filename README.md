# Garso signalų apdorojimas
## 1. Garso signalų atvaizdavimas

Programa naudoja `scipy.io wavfilw` biblioteką `*.wav` tipo audio failams nuskaityti.  

Nuskaityto failo duomenys atvaizduojami naudojami `matplotlib` biblioteką. Programa nustato audio failo kanalų skaičių, diskretizavimo dažnį (kilohercais) bei kvantavimo gylį (bitais).  

### Naudojimasis programa

1. Paleidus programą, iššoka standartinio failo pasirinkimo dialogas, kurio pagalba, pasirenkamas norimas `*.wav` tipo failas.
2. Tuomet komandinėje eilutėje nurodoma žymeklio pozicija laike, garso įrašo trukmės ribose. Jei garso įrašo trukmė nesiekia minutės, nurodomos sekundės, kitu atveju - minutės ir sekundės.
3. Pateikiama diagrama, kurioje atvaizduojamas garso įrašas, kartu su esminiais parametrais, bei žymeklis pasirinktoje vietoje.

## 2. Garso signalų analizė laiko srityje

