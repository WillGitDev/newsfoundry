"use client";
import { useState, useEffect } from "react";
import { apiFetch } from "@/libs/api";

export function useChat(path) {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const result = await apiFetch(path);
        setMessages(result.messages);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };
    if (path) {
      load();
    } else {
      setLoading(false);
    }
  }, [path]);
  return { messages, loading, error };
}
