"use client";
import { useState } from "react";
import styles from "./page.module.css";
import toast from "react-hot-toast";
import Logo from "@components/Logo";
import { useRouter } from "next/navigation";

export default function Home() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const router = useRouter();
  const handleLogin = async (e) => {
    e.preventDefault();
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      toast.error("Email ou mot de passe incorrect", { duration: 20000 });
      return;
    }
    const data = await response.json();
    localStorage.setItem("token", data.token);
    router.push("/HomeChat");
  };

  return (
    <div className={styles.page}>
      <div className={styles.container}>
        <Logo />
        <h2 className={styles.h2}>
          Connectez-vous pour accéder à votre assistant d'actualités IA
        </h2>
        <form className={styles.form} onSubmit={handleLogin}>
          <label htmlFor="email" className={styles.label}>
            Adresse email
          </label>
          <input
            type="text"
            id="email"
            name="email"
            className={styles.input}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            aria-required="true"
            placeholder="votre email@exemple.com"
          />
          <label htmlFor="password" className={styles.label}>
            Mot de passe
          </label>
          <input
            type="password"
            id="password"
            name="password"
            className={styles.input}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            aria-required
            placeholder="votre mot de passe"
          />
          <button type="submit" className={styles.submit}>
            Se connecter
          </button>
        </form>
      </div>
    </div>
  );
}
