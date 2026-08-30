"use client";
import styles from "./chatThreadHeader.module.css";
import { useRouter } from "next/navigation";
import { useState } from "react";
import * as Dialog from "@radix-ui/react-dialog";
import { apiFetch } from "@/libs/api";
import { toast } from "react-hot-toast";

export default function ChatThreadHeader({ chatTitle, chatId }) {
  const [sujetRevue, setSujetRevue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  const handleBack = () => {
    router.push("/HomeChat");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      await apiFetch(`/chats/${chatId}/revue`, {
        method: "POST",
        body: JSON.stringify({ sujet: sujetRevue }),
      });
      router.push("/HomeChat/revues");
    } catch (err) {
      toast.error(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.header}>
      <div className={styles.backContainer}>
        <button
          type="button"
          aria-label="Retour"
          className={styles.backButton}
          onClick={handleBack}
        >
          <svg
            width="19"
            height="8"
            viewBox="0 0 19 8"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M0.146446 3.32833C-0.0488148 3.52359 -0.0488148 3.84017 0.146446 4.03544L3.32843 7.21742C3.52369 7.41268 3.84027 7.41268 4.03553 7.21742C4.2308 7.02216 4.2308 6.70557 4.03553 6.51031L1.20711 3.68188L4.03553 0.853456C4.2308 0.658194 4.2308 0.341612 4.03553 0.14635C3.84027 -0.0489126 3.52369 -0.0489126 3.32843 0.14635L0.146446 3.32833ZM18.5 3.68188L18.5 3.18188L0.5 3.18188L0.5 3.68188L0.5 4.18188L18.5 4.18188L18.5 3.68188Z"
              fill="currentColor"
            />
          </svg>
        </button>
        <div>
          <p className={styles.chatTitle}>
            {chatTitle || "Nouvelle discussion"}
          </p>
          <p className={styles.infoConv}>Conversation active</p>
        </div>
      </div>
      <Dialog.Root>
        <Dialog.Trigger asChild>
          <button type="button" className={styles.button}>
            <svg
              width="12"
              height="15"
              viewBox="0 0 12 15"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M8.13086 0.0136719C8.25885 0.039297 8.37799 0.101683 8.47168 0.195312L11.8047 3.5293C11.9296 3.65417 11.9998 3.82342 12 4V12.667C12 13.1973 11.7889 13.706 11.4141 14.0811C11.0391 14.4559 10.5302 14.6669 10 14.667H2C1.46968 14.6669 0.960933 14.4561 0.585938 14.0811C0.210966 13.706 1.89365e-07 13.1973 0 12.667V2C0.000172407 1.4698 0.211018 0.960857 0.585938 0.585938C0.960903 0.211145 1.46984 8.61611e-05 2 0H8L8.13086 0.0136719ZM2 1.33398C1.82346 1.33407 1.65421 1.40455 1.5293 1.5293C1.40443 1.65417 1.33416 1.82342 1.33398 2V12.667C1.33398 12.8438 1.40427 13.0136 1.5293 13.1387C1.65421 13.2634 1.82346 13.3339 2 13.334H10C10.1766 13.3339 10.3467 13.2635 10.4717 13.1387C10.5965 13.0137 10.667 12.8436 10.667 12.667V5.33398H8.66602C8.13582 5.33381 7.62687 5.12297 7.25195 4.74805C6.87716 4.37308 6.6661 3.86415 6.66602 3.33398V1.33398H2ZM8.66602 10C9.0341 10 9.33283 10.299 9.33301 10.667C9.33301 11.0352 9.03421 11.334 8.66602 11.334H3.33301C2.96497 11.3338 2.66602 11.0351 2.66602 10.667C2.66619 10.2991 2.96508 10.0002 3.33301 10H8.66602ZM8.66602 7.33398C9.03421 7.33398 9.33301 7.63279 9.33301 8.00098C9.33283 8.36902 9.0341 8.66797 8.66602 8.66797H3.33301C2.96508 8.66779 2.66619 8.36891 2.66602 8.00098C2.66602 7.6329 2.96497 7.33416 3.33301 7.33398H8.66602ZM4.66602 4.66699C5.03421 4.66699 5.33301 4.96579 5.33301 5.33398C5.33301 5.70217 5.03421 6.00098 4.66602 6.00098H3.33301C2.96497 6.0008 2.66602 5.70207 2.66602 5.33398C2.66602 4.9659 2.96497 4.66717 3.33301 4.66699H4.66602ZM8 3.33398C8.00009 3.51052 8.07057 3.67977 8.19531 3.80469C8.32018 3.92956 8.48944 3.99983 8.66602 4H10.3906L8 1.60938V3.33398Z"
                fill="currentColor"
              />
            </svg>
            Générer une revue de presse
          </button>
        </Dialog.Trigger>
        <Dialog.Portal>
          <Dialog.Overlay className={styles.backgroundPage} />
          <Dialog.Content className={styles.contentModal}>
            <Dialog.Close asChild className={styles.closeContainer}>
              <button className={styles.closeModal}>Fermer</button>
            </Dialog.Close>
            <Dialog.Title className={styles.titleModal}>
              Générer une revue de presse
            </Dialog.Title>
            <Dialog.Description className={styles.description}>
              Donner un titre à votre revue de presse
            </Dialog.Description>
            <form className={styles.form} onSubmit={handleSubmit}>
              <label htmlFor="nameRevue" className={styles.label}>
                Thème de la revue de presse
              </label>
              <input
                type="text"
                id="nameRevue"
                name="nameRevue"
                value={sujetRevue}
                onChange={(e) => setSujetRevue(e.currentTarget.value)}
                className={`${styles.inputText} ${styles.champ}`}
              />
              <button
                type="submit"
                className={`${styles.buttonSubmit} ${styles.champ}`}
              >
                Générer
              </button>
            </form>
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>
    </div>
  );
}
