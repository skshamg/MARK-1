import sys
from core.brain import Mark1Brain
from core.speech import SpeechEngine

def main():
    print("\n" + "=" * 55)
    print("      MARK-1 // AUTONOMOUS SYSTEM CORE ONLINE")
    print("=" * 55)
    print("Initializing neural handshake, vocal synthesis, and memory...")

    speaker = SpeechEngine()
    brain = Mark1Brain()

    print(f"Active Link: {brain.active_model}")
    print("Ready for instructions.")
    print("Type 'exit' or 'quit' to shut down Mark-1.\n")

    # Vocal confirmation on boot
    speaker.speak("Mark One online. All systems nominal, sir.")

    while True:
        try:
            # Notice the prompt here: simply type your instruction after USER >
            user_prompt = input("USER > ").strip()
            
            if not user_prompt:
                continue

            if user_prompt.lower() in ["exit", "quit", "shutdown"]:
                farewell = "Shutting down systems. Goodbye, sir."
                print(f"\nMARK-1 > {farewell}\n")
                speaker.speak(farewell)
                break

            # 1. Ask the AI brain
            reply = brain.talk(user_prompt)
            print(f"\nMARK-1 > {reply}\n")

            # 2. Speak the AI's actual dynamic reply aloud
            speaker.speak(reply)

        except KeyboardInterrupt:
            print("\n\nMARK-1: Emergency abort detected. Standing down.")
            break

if __name__ == "__main__":
    main()