import { useState, useEffect } from "react";

export default function useTypingEffect(text, speed = 15) {
  const [displayedText, setDisplayedText] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    if (!text) {
      setDisplayedText("");
      setIsTyping(false);
      return;
    }

    setIsTyping(true);
    setDisplayedText("");

    let currentIndex = 0;
    const characters = Array.from(text);

    const interval = setInterval(() => {
      const chunkSize = Math.random() < 0.3 ? 12 : 8;
      
      currentIndex = Math.min(currentIndex + chunkSize, characters.length);
      setDisplayedText(characters.slice(0, currentIndex).join(""));

      if (currentIndex >= characters.length) {
        clearInterval(interval);
        setIsTyping(false);
      }
    }, speed);

    return () => {
      clearInterval(interval);
    };
  }, [text, speed]);

  return { displayedText, isTyping };
}
