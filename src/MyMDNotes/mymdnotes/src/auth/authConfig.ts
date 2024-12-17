import { Configuration, IPublicClientApplication, PublicClientApplication } from "@azure/msal-browser";

const msalConfig: Configuration = {
    auth: {
        clientId: "0277e530-0a6d-4eaa-a3f8-3422ba367bb5",
    authority: `https://login.microsoftonline.com/zionclouds.com`, //e28d23e3-803d-418d-a720-c0bed39f77b6
    redirectUri: "http://localhost:5173/",
    postLogoutRedirectUri: 'https://zionai.com/about-us/',
    },
    cache: {
        cacheLocation: "localStorage"
    }
};

export const msalInstance: IPublicClientApplication = new PublicClientApplication(msalConfig);