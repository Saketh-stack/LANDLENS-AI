// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";

// Your web app's Firebase configuration
export const firebaseConfig = {
  apiKey: "AIzaSyCZSobevg0U48zqscNgrHP27URNqTeLpKE",
  authDomain: "landlens-ai-56a07.firebaseapp.com",
  projectId: "landlens-ai-56a07",
  storageBucket: "landlens-ai-56a07.firebasestorage.app",
  messagingSenderId: "142577012396",
  appId: "1:142577012396:web:124ef2bd27b6e06f549909",
  measurementId: "G-XKS4GT0W35"
};

// Initialize Firebase
export const app = initializeApp(firebaseConfig);
export const analytics = typeof window !== 'undefined' ? getAnalytics(app) : null;
