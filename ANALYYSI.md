# Analyysi
1. Mitä tekoäly teki hyvin?
   - Antoi hyvät vaihtoehdot frameworkeihin ja hyvän ensimmäisen arvauksen/toteutuksen.
   - Kun pyydetty asia on tarpeeksi hyvin rajattu ja tarpeeksi pieni, niin tulokset ovat hyviä.
2. Mitä tekoäly teki huonosti?
   - Koko projekti oli käytännössä laitettu yhteen tiedostoon.
   - Joitain tosielämän logiikkapuutteita, kuten huoneiden yksilöinti ja validointi puuttui.
   - Joitain yksittäisiä asioita, joita tekoäly hallusinoi tai arvasi, kun kontekstia ja määrittelyä ei ollut tarpeeksi.
3. Mitkä olivat tärkeimmät parannukset, jotka teit tekoälyn tuottamaan koodiin ja miksi?
   - Ohjailin jo käytön aikana tekoälyä sekä iteroin tuloksia, sillä tämä on suositeltua: https://docs.github.com/en/copilot/concepts/prompting/prompt-engineering . Lopuksi ei tarvinnut niin paljoa korjailla/muokata koodia.
   - Suurin muutos oli ottaa huone_id:t mukaan toteutukseen.