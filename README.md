# Garso signalų apdorojimas
## 1. Garso signalų atvaizdavimas bei analizė laiko srityje

Programa naudoja `scipy.io wavfile` biblioteką `*.wav` tipo audio failams nuskaityti.  

Nuskaityto failo duomenys atvaizduojami naudojami `matplotlib` biblioteką. Programa nustato audio failo kanalų skaičių, diskretizavimo dažnį (kilohercais) bei kvantavimo gylį (bitais). Taip pat galima apskaičiuoti signalo energiją bei nulio kirtimų skaičių.

### Naudojimasis programa

1. Paleidus programą, komandinėje eilutėje pateikiamas programos meniu. Pasirinkus pirmą variantą "Open file", iššoka standartinio failo pasirinkimo dialogas, kurio pagalba pasirenkamas norimas `*.wav` tipo failas. Norint baigti programos darbą pasirenkamas "Quit" variantas.
```
MENU
 [1] Open file
 [2] Quit
> 
```
2. Toliau reikia pasirinkti kokio tipo diagramą braižyti, arba grįžti į pagrindinį meniu.
```
FILE 'Filename.wav' MENU
 [1] Energy plot
 [2] ZCR plot
 [3] Time plot
 [4] Segment plot
 [5] Fade effect
 [6] Menu
> 
```
3. Pasirinkus `Energy` ir `ZCR` diagramas, reikia papildomai nurodyti šių parametrų skaičiavimui naudojamo kadro ilgį milisekundėmis.
```
> 1
Enter frame size in ms.
> 
```
Pasirinkus `Segment` diagramą reikia nurodyti kadro ilgį bei segmentavimo slenkčio vertę.
```
> 4
Enter frame size in ms.
> 
Enter step size.
> 
```
Pasirinkus `Time` diagramą, pasirinktoje vietoje papildomai nurodomas žymeklio laikas.
```
> 3
Audio length: 00:01.498
Enter marker time.
Seconds:
> 
```
Pasirinkus `Fade effect`, reikia nurodyti *fade* efekto trukmę ir pasirinkti kitimo dėsnį.
```
Audio length: 00:01.498
Enter fade time in ms:
> 100
Choose fade type:
[1] Linear
[2] Logarithmic
>
```
4. Pateikiama diagrama, kurioje atvaizduojamas garso įrašas, kartu su esminiais parametrais. Pvz:
```
MENU
 [1] Open file
 [2] Quit
> 1
Processing...
FILE 'Elephant.wav' MENU
 [1] Energy plot
 [2] ZCR plot
 [3] Time plot
 [4] Segment plot
 [5] Fade effect
 [6] Menu
> 1
Enter frame size in ms.
> 20
```
![energy plot of Elephant.wav file](plots/elephant_energy_20.png)