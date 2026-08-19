"use client";
import styles from "./pastChat.module.css";
import DiscussionItem from "@components/DiscussionItem";
import Logo from "@components/Logo";
import { useFetch } from "@/hooks/useFetch";
import { useEffect } from "react";
import { toast } from "react-hot-toast";

export default function PastChat() {
  const { data: chats, loading, error } = useFetch("/chats"); // Renomme data en chats.
  useEffect(() => {
    if (error) {
      toast.error(error.message);
    }
  }, [error]);
  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <Logo />
      </div>
      <div className={styles.pastChatContainer}>
        {loading && <p>Chargement...</p>}
        {chats?.map((chat) => (
          <DiscussionItem key={chat.id} id={chat.id} date={chat.created_at} />
        ))}
      </div>
      <div className={styles.logoutContainer}>
        <p>Se déconnecter</p>
      </div>
    </div>
  );
}
