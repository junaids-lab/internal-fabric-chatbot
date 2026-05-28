let msalClient;
let activeAccount;
let frontendConfig;

const statusEl = document.getElementById("status");
const messagesEl = document.getElementById("messages");
const signInButton = document.getElementById("signInButton");
const signOutButton = document.getElementById("signOutButton");
const sendButton = document.getElementById("sendButton");
const chatForm = document.getElementById("chatForm");
const questionInput = document.getElementById("questionInput");
const localeInput = document.getElementById("localeInput");

init();

async function init() {
  frontendConfig = await loadFrontendConfig();

  if (!frontendConfig.clientId || !frontendConfig.tenantId) {
    setStatus("Missing ENTRA_FRONTEND_CLIENT_ID or ENTRA_TENANT_ID in backend configuration.");
    signInButton.disabled = true;
    return;
  }

  msalClient = new msal.PublicClientApplication({
    auth: {
      clientId: frontendConfig.clientId,
      authority: `https://login.microsoftonline.com/${frontendConfig.tenantId}`,
      redirectUri: window.location.origin,
    },
    cache: {
      cacheLocation: "sessionStorage",
    },
  });

  await msalClient.handleRedirectPromise();
  const accounts = msalClient.getAllAccounts();
  if (accounts.length > 0) {
    setActiveAccount(accounts[0]);
  }
}

async function loadFrontendConfig() {
  const response = await fetch("/frontend-config");
  if (!response.ok) {
    throw new Error("Unable to load frontend configuration.");
  }
  return response.json();
}

signInButton.addEventListener("click", async () => {
  try {
    const loginResult = await msalClient.loginPopup({
      scopes: frontendConfig.powerbiScopes,
    });
    setActiveAccount(loginResult.account);
  } catch (error) {
    addMessage("error", readableError(error));
  }
});

signOutButton.addEventListener("click", async () => {
  if (!activeAccount) {
    return;
  }
  await msalClient.logoutPopup({ account: activeAccount });
  activeAccount = undefined;
  setStatus("Not signed in");
  signInButton.disabled = false;
  signOutButton.disabled = true;
  sendButton.disabled = true;
});

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const question = questionInput.value.trim();
  if (!question) {
    return;
  }

  addMessage("user", question);
  questionInput.value = "";
  sendButton.disabled = true;

  try {
    const token = await acquirePowerBiToken();
    const response = await fetch("/chat", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question,
        locale: localeInput.value || null,
        filters: {},
      }),
    });

    const body = await response.json();
    if (!response.ok) {
      throw new Error(JSON.stringify(body, null, 2));
    }

    addMessage("assistant", body.answer);
  } catch (error) {
    addMessage("error", readableError(error));
  } finally {
    sendButton.disabled = !activeAccount;
  }
});

async function acquirePowerBiToken() {
  if (!activeAccount) {
    throw new Error("Please sign in first.");
  }

  const request = {
    account: activeAccount,
    scopes: frontendConfig.powerbiScopes,
  };

  try {
    const response = await msalClient.acquireTokenSilent(request);
    return response.accessToken;
  } catch (error) {
    const response = await msalClient.acquireTokenPopup(request);
    return response.accessToken;
  }
}

function setActiveAccount(account) {
  activeAccount = account;
  msalClient.setActiveAccount(account);
  setStatus(`Signed in as ${account.username}`);
  signInButton.disabled = true;
  signOutButton.disabled = false;
  sendButton.disabled = false;
}

function setStatus(text) {
  statusEl.textContent = text;
}

function addMessage(kind, text) {
  const node = document.createElement("div");
  node.className = `message ${kind}`;
  node.textContent = text;
  messagesEl.appendChild(node);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function readableError(error) {
  return error?.message || String(error);
}
