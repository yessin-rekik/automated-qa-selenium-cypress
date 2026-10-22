# Rapport d'execution - Web Tours

- Date : 22/10/2026 13:55
- Outil : PyTest + Selenium WebDriver (Chrome headless)
- Application : Web Tours - http://127.0.0.1:1080/WebTours/index.htm
- Plan de test Xray : **WT-65**

## Synthese

| Resultat | Nombre |
|---|---|
| PASSED | 31 |
| FAILED (defauts confirmes) | 14 |
| Total | 45 |

Taux de reussite : **68.9 %**

## Par dossier

| Dossier | PASSED | FAILED |
|---|---|---|
| /BT | 4 | 4 |
| /ET/Authentification | 6 | 0 |
| /ET/Paiement | 0 | 4 |
| /ET/Recherche | 0 | 4 |
| /FT | 1 | 0 |
| /FT/Authentification | 5 | 0 |
| /FT/Itineraire | 4 | 0 |
| /FT/Recherche | 4 | 0 |
| /FT/Reservation | 4 | 0 |
| /PT | 3 | 2 |

## Detail des tests

| ID | Test | Dossier | Story | Xray | Resultat |
|---|---|---|---|---|---|
| FT-00 | `test_ft_00_application_is_available` | /FT | - | WT-20 | **PASS** |
| FT-01 | `test_ft_01_login_with_valid_credentials` | /FT/Authentification | WT-7 | WT-21 | **PASS** |
| FT-02 | `test_ft_02_logged_in_user_sees_main_menu` | /FT/Authentification | WT-7 | WT-22 | **PASS** |
| FT-03 | `test_ft_03_sign_off_returns_to_login` | /FT/Authentification | WT-8 | WT-23 | **PASS** |
| FT-04 | `test_ft_04_register_then_login` | /FT/Authentification | WT-6 | WT-24 | **PASS** |
| FT-05 | `test_ft_05_home_page_welcomes_the_user` | /FT/Authentification | WT-7 | WT-25 | **PASS** |
| FT-06 | `test_ft_06_search_flights_one_way` | /FT/Recherche | WT-9 | WT-26 | **PASS** |
| FT-07 | `test_ft_07_search_flights_roundtrip` | /FT/Recherche | WT-10 | WT-27 | **PASS** |
| FT-08 | `test_ft_08_city_lists_are_complete` | /FT/Recherche | WT-9 | WT-28 | **PASS** |
| FT-09 | `test_ft_09_seat_and_class_options_are_available` | /FT/Recherche | WT-11 | WT-29 | **PASS** |
| FT-10 | `test_ft_10_complete_booking_shows_invoice` | /FT/Reservation | WT-13 | WT-30 | **PASS** |
| FT-11 | `test_ft_11_invoice_contains_payment_information` | /FT/Reservation | WT-14 | WT-31 | **PASS** |
| FT-12 | `test_ft_12_total_depends_on_passenger_count` | /FT/Reservation | WT-13 | WT-32 | **PASS** |
| FT-13 | `test_ft_13_seat_class_is_used_in_invoice` | /FT/Reservation | WT-11 | WT-33 | **PASS** |
| FT-14 | `test_ft_14_booking_appears_in_itinerary` | /FT/Itineraire | WT-16 | WT-34 | **PASS** |
| FT-15 | `test_ft_15_cancel_a_single_reservation` | /FT/Itineraire | WT-17 | WT-35 | **PASS** |
| FT-16 | `test_ft_16_cancel_all_reservations` | /FT/Itineraire | WT-18 | WT-36 | **PASS** |
| FT-17 | `test_ft_17_empty_itinerary_message` | /FT/Itineraire | WT-16 | WT-37 | **PASS** |
| ET-01 | `test_et_01_wrong_password` | /ET/Authentification | WT-7 | WT-38 | **PASS** |
| ET-02 | `test_et_02_unknown_user` | /ET/Authentification | WT-7 | WT-39 | **PASS** |
| ET-03 | `test_et_03_empty_credentials_are_rejected` | /ET/Authentification | WT-7 | WT-40 | **PASS** |
| ET-04 | `test_et_04_registration_password_mismatch` | /ET/Authentification | WT-6 | WT-41 | **PASS** |
| ET-05 | `test_et_05_registration_duplicate_username` | /ET/Authentification | WT-6 | WT-42 | **PASS** |
| ET-06 | `test_et_06_registration_non_alphanumeric_username` | /ET/Authentification | WT-6 | WT-43 | **PASS** |
| ET-07 | `test_et_07_invalid_date_format_is_rejected` | /ET/Recherche | WT-12 | WT-44 | **FAIL** |
| ET-08 | `test_et_08_past_departure_date_is_rejected` | /ET/Recherche | WT-12 | WT-45 | **FAIL** |
| ET-09 | `test_et_09_same_departure_and_arrival_city_is_rejected` | /ET/Recherche | WT-12 | WT-46 | **FAIL** |
| ET-10 | `test_et_10_return_before_departure_is_rejected` | /ET/Recherche | WT-12 | WT-47 | **FAIL** |
| ET-11 | `test_et_11_payment_without_credit_card_is_rejected` | /ET/Paiement | WT-15 | WT-48 | **FAIL** |
| ET-12 | `test_et_12_payment_with_non_numeric_card_is_rejected` | /ET/Paiement | WT-15 | WT-49 | **FAIL** |
| ET-13 | `test_et_13_payment_with_invalid_expiration_month_is_rejected` | /ET/Paiement | WT-15 | WT-50 | **FAIL** |
| ET-14 | `test_et_14_payment_with_empty_first_name_is_rejected` | /ET/Paiement | WT-15 | WT-51 | **FAIL** |
| BT-01 | `test_bt_01_username_is_limited_to_14_characters` | /BT | WT-6 | WT-52 | **PASS** |
| BT-02 | `test_bt_02_credit_card_is_limited_to_20_characters` | /BT | WT-15 | WT-53 | **PASS** |
| BT-03 | `test_bt_03_one_passenger_is_the_lower_valid_boundary` | /BT | WT-12 | WT-54 | **PASS** |
| BT-04 | `test_bt_04_zero_passenger_is_rejected` | /BT | WT-12 | WT-55 | **FAIL** |
| BT-05 | `test_bt_05_non_numeric_passenger_count_is_rejected` | /BT | WT-12 | WT-56 | **FAIL** |
| BT-06 | `test_bt_06_eight_passengers_is_the_upper_input_boundary` | /BT | WT-12 | WT-57 | **PASS** |
| BT-07 | `test_bt_07_huge_passenger_count_is_rejected` | /BT | WT-12 | WT-58 | **FAIL** |
| BT-08 | `test_bt_08_non_existent_date_is_rejected` | /BT | WT-12 | WT-59 | **FAIL** |
| PT-01 | `test_pt_01_itinerary_requires_authentication` | /PT | WT-19 | WT-60 | **FAIL** |
| PT-02 | `test_pt_02_flight_search_requires_authentication` | /PT | WT-19 | WT-61 | **FAIL** |
| PT-03 | `test_pt_03_anonymous_profile_page_does_not_leak_session` | /PT | WT-19 | WT-62 | **PASS** |
| PT-04 | `test_pt_04_users_cannot_see_each_others_reservations` | /PT | WT-19 | WT-63 | **PASS** |
| PT-05 | `test_pt_05_reservations_are_not_available_after_sign_off` | /PT | WT-19 | WT-64 | **PASS** |

## Defauts confirmes

- **BT-04** (`test_bt_04_zero_passenger_is_rejected`) : BUG-02: nombre de passagers 0 accepte
- **BT-05** (`test_bt_05_non_numeric_passenger_count_is_rejected`) : BUG-02: nombre de passagers non numerique accepte
- **BT-07** (`test_bt_07_huge_passenger_count_is_rejected`) : BUG-02: 999 passagers acceptes sans limite
- **BT-08** (`test_bt_08_non_existent_date_is_rejected`) : BUG-01: 29/02/2025 accepte sans message
- **ET-07** (`test_et_07_invalid_date_format_is_rejected`) : BUG-01: date invalide acceptee sans message d'erreur
- **ET-08** (`test_et_08_past_departure_date_is_rejected`) : BUG-01: date de depart passee acceptee
- **ET-09** (`test_et_09_same_departure_and_arrival_city_is_rejected`) : BUG-01: ville de depart = ville d'arrivee acceptee
- **ET-10** (`test_et_10_return_before_departure_is_rejected`) : BUG-01: date de retour anterieure au depart acceptee
- **ET-11** (`test_et_11_payment_without_credit_card_is_rejected`) : BUG-03: paiement accepte sans numero de carte
- **ET-12** (`test_et_12_payment_with_non_numeric_card_is_rejected`) : BUG-03: carte non numerique acceptee
- **ET-13** (`test_et_13_payment_with_invalid_expiration_month_is_rejected`) : BUG-03: mois d'expiration 13 accepte
- **ET-14** (`test_et_14_payment_with_empty_first_name_is_rejected`) : BUG-03: nom vide accepte au paiement
- **PT-01** (`test_pt_01_itinerary_requires_authentication`) : BUG-04: itinerary.pl accessible sans session
- **PT-02** (`test_pt_02_flight_search_requires_authentication`) : BUG-04: reservations.pl accessible sans session

## Analyse

- Le parcours fonctionnel nominal (connexion, recherche, reservation, itineraire, annulation) fonctionne : tous les tests FT passent.
- Les tests d'erreur, aux limites et de permissions revelent 5 defauts (WT-67 a WT-71), principalement l'absence de validation cote serveur et l'absence de controle de session sur les pages CGI.
- La validation cote client (fichiers `chooseFlightValidate.js` et `purchaseValidate.js`) existe mais n'est pas activee : les formulaires sont generes avec `onsubmit=""`, donc aucune verification n'est executee avant l'envoi.
- Les tests marques `xfail` dans la suite documentent ces defauts : ils passeront automatiquement lorsque l'application sera corrigee.

## Artefacts

- Rapport HTML : `webtours-tests/reports/report.html`
- JUnit XML (Jenkins) : `webtours-tests/reports/junit.xml`
- Captures d'ecran des echecs : `webtours-tests/reports/screenshots/`
- Execution Xray : voir le Test Execution lie au plan WT-65
