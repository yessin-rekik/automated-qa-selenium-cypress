// Suite Cypress de comparaison : memes cas que la suite Selenium/PyTest
// (meme identifiant de test), pour comparer les deux outils.

describe("Web Tours - Cypress", () => {
  let user;

  beforeEach(() => {
    cy.register().then((u) => { user = u; });
  });

  it("FT-00 l'application est disponible (index + page CGI)", () => {
    cy.request("/WebTours/index.htm").its("body").should("contain", "Web Tours");
    cy.request("/cgi-bin/welcome.pl?signOff=true").its("status").should("eq", 200);
  });

  it("FT-01 connexion avec des identifiants valides", () => {
    cy.openApp();
    cy.login(user.username, user.password);
    cy.frame("info", "welcome,").should("contain.text", user.username);
  });

  it("FT-06 recherche d'un vol aller simple : 4 vols proposes", () => {
    cy.openApp();
    cy.login(user.username, user.password);
    cy.frame("info", "welcome,");
    cy.searchOneWay();
    cy.frame("info", "Flight departing from")
      .find("input[name=outboundFlight]")
      .should("have.length", 4);
  });

  it("FT-10 reservation complete : facture affichee", () => {
    cy.openApp();
    cy.login(user.username, user.password);
    cy.frame("info", "welcome,");
    cy.searchOneWay();
    cy.frame("info", "Flight departing from").within(() => {
      cy.get("input[name=outboundFlight]").first().check();
      cy.get("input[name=reserveFlights]").click();
    });
    cy.frame("info", "Payment Details").within(() => {
      cy.get("input[name=creditCard]").clear().type("12345678");
      cy.get("input[name=expDate]").clear().type("12/30");
      cy.get("input[name=buyFlights]").click();
    });
    cy.frame("info", "Thank you for booking through Web Tours");
  });

  it("ET-01 mot de passe incorrect refuse", () => {
    cy.openApp();
    cy.login(user.username, "definitely-wrong");
    cy.frame("info", "error").should("contain.text", "Incorrect Password");
  });

  // Cypress n'a pas d'equivalent du xfail PyTest : ce test verifie le
  // comportement actuel (defaut BUG-04 / WT-70) et echouera si le defaut est corrige.
  it("PT-01 [BUG-04] itinerary.pl est servi sans session (defaut confirme)", () => {
    cy.request({ url: "/cgi-bin/itinerary.pl", followRedirect: false, failOnStatusCode: false })
      .then((r) => {
        expect(r.status, "aucune redirection vers la connexion").to.eq(200);
        expect(String(r.body)).to.contain("Itinerary");
      });
  });
});
