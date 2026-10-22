// Commandes partagees : equivalent Cypress du page object Selenium (webtours/app.py).
// L'application est un frameset : index.htm > frame "body" > frames
// "navbar" (menu) et "info" (contenu). Cypress n'a pas d'API de frames,
// on passe donc par contentDocument (meme origine).

const PASSWORD = "Passw0rd";

// Renvoie le <body> de la frame body > name une fois charge, en attendant
// eventuellement un texte (re-interroge a chaque appel, comme _goto en Python).
Cypress.Commands.add("frame", (name, text) => {
  return cy
    .get('frame[name="body"]')
    .should(($outer) => {
      const outer = $outer[0].contentDocument;
      const inner = outer && outer.querySelector(`frame[name="${name}"]`);
      const body = inner && inner.contentDocument && inner.contentDocument.body;
      expect(body, `frame ${name}`).to.exist;
      if (text) {
        expect(body.innerText.toLowerCase()).to.contain(text.toLowerCase());
      } else {
        expect(body.innerHTML).not.to.equal("");
      }
    })
    .then(($outer) => {
      const inner = $outer[0].contentDocument.querySelector(`frame[name="${name}"]`);
      return cy.wrap(inner.contentDocument.body);
    });
});

Cypress.Commands.add("openApp", () => {
  cy.visit("/WebTours/index.htm");
  cy.frame("navbar").find("input[name=username]").should("exist");
});

// Cree un compte via le formulaire d'inscription (comme api.register en Python).
Cypress.Commands.add("register", (prefix = "cy") => {
  const username = `${prefix}${Math.random().toString(16).slice(2, 10)}`.slice(0, 14);
  return cy
    .request({
      method: "POST",
      url: "/cgi-bin/login.pl",
      form: true,
      body: {
        "register.x": "1", username, password: PASSWORD, passwordConfirm: PASSWORD,
        firstName: "Web", lastName: "Tours", address1: "1 Rue de la Paix", address2: "Tunis",
      },
    })
    .then(() => ({ username, password: PASSWORD }));
});

Cypress.Commands.add("login", (username, password) => {
  cy.frame("navbar").within(() => {
    cy.get("input[name=username]").clear().type(username);
    cy.get("input[name=password]").clear().type(password, { log: false });
    cy.get("input[name=login]").click();
  });
});

Cypress.Commands.add("menu", (alt) => {
  cy.frame("navbar").find(`img[alt="${alt}"]`).click();
});

function future(days) {
  const d = new Date();
  d.setDate(d.getDate() + days);
  const pad = (n) => String(n).padStart(2, "0");
  return `${pad(d.getMonth() + 1)}/${pad(d.getDate())}/${d.getFullYear()}`;
}

// Recherche aller simple Denver -> Frankfurt (meme jeu de donnees que Selenium).
Cypress.Commands.add("searchOneWay", (passengers = 1) => {
  cy.menu("Search Flights Button");
  cy.frame("info", "Find Flight").within(() => {
    cy.get("select[name=depart]").select("Denver");
    cy.get("select[name=arrive]").select("Frankfurt");
    cy.get("input[name=departDate]").clear().type(future(2));
    cy.get("input[name=numPassengers]").clear().type(String(passengers));
    cy.get("input[name=roundtrip]").uncheck();
    cy.get("input[name=findFlights]").click();
  });
});
