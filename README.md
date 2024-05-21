# Fast and Furious - multiplayer game

Fast and Furious to prosta gra stworzona w języku Python z wykorzystaniem biblioteki Pygame. Gra polega na sterowaniu samochodami i zbieraniu pieniędzy na drodze, unikając przy tym kolizji z innymi pojazdami.

## Jak uruchomić grę?

1. Upewnij się, że masz zainstalowaną bibliotekę Pygame. Jeśli nie, możesz ją zainstalować za pomocą pip:

   ```
   pip install pygame
   ```

2. Po zainstalowaniu Pygame, uruchom plik `main.py`.

## Stosowane Mutexy:

W grze Fast and Furious wykorzystywane są mutexy do synchronizacji dostępu do wspólnych zasobów przez różne wątki. Mutexy są używane w celu zapewnienia bezpiecznego dostępu do listy samochodów i listy pieniędzy. Dzięki temu unikamy wyścigów (race conditions) i zapewniamy spójność danych w grze.

- Mutex dla listy samochodów (CarThread): Wątek generujący samochody (CarThread) korzysta z mutexu, aby synchronizować dostęp do listy samochodów. Mutex zapewnia, że tylko jeden wątek naraz może dodawać nowe samochody do listy, co eliminuje możliwość konfliktów przy dostępie do wspólnego zasobu.

- Mutex dla listy pieniędzy (CashThread): Podobnie jak w przypadku samochodów, wątek generujący pieniądze (CashThread) korzysta z mutexu, aby synchronizować dostęp do listy pieniędzy na drodze. Dzięki mutexowi zapewniamy bezpieczny dostęp do tej listy, eliminując możliwość równoczesnego dostępu przez wiele wątków.
## Instrukcje gry:

- Po uruchomieniu gry, możesz rozpocząć grę, klikając przycisk "Start".
- Sterowanie:
  - Gracz 1:
    - Góra: Strzałka w górę
    - Dół: Strzałka w dół
    - Lewo: Strzałka w lewo
    - Prawo: Strzałka w prawo
  - Gracz 2:
    - Góra: Klawisz "W"
    - Dół: Klawisz "S"
    - Lewo: Klawisz "A"
    - Prawo: Klawisz "D"
- Celem gry jest zbieranie pieniędzy na drodze, unikając kolizji z innymi samochodami. 
- W pojedynczej grze pieniądze otrzymuje tylko gracz, którego auto wygrało. 
- Gra kończy się, gdy którykolwiek z graczy stłucze swój samochód. 
- Po zakończeniu gry możesz zrestartować grę lub zakończyć działanie programu. 
- Wyniki zapisywane są do pliku tekstowego "baza.txt". Możesz tam kontrolować, kto wygrywa w kolejnych rozgrywkach.

## Zdjęcia z gry:

[//]: # (![Start Screen]&#40;screenshots/start_screen.png&#41;)
*Ekran startowy gry*

[//]: # (![Gameplay]&#40;screenshots/gameplay.png&#41;)
*Gameplay*

[//]: # (![Game Over Screen]&#40;screenshots/game_over.png&#41;)
*Ekran zakończenia gry*

## Autorzy:

- Klaudia Marzec
- Zakia Shefa 




