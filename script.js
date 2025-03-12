const messages = document.getElementById("messages");
const userInput = document.getElementById("userInput");
const synth = window.speechSynthesis;
const voiceModeBtn = document.getElementById("voiceModeBtn");
const textModeBtn = document.getElementById("textModeBtn");
const chatbot = document.getElementById("chatbot");
const chatbox = document.getElementById("chatbox");
const blinkBox = document.getElementById("blinkBox");
const recordBtn = document.getElementById("recordBtn");
const sendBtn = document.getElementById("sendBtn");
// const blinkTable = document.getElementById("blinkTable");
const gameBox = document.getElementById("gameBox");
const exitBtn = document.getElementById("exitBtn");
var _currentIndex = 1;

const r = new rive.Rive({
  src: "./assets/py_chatbot.riv",
  canvas: document.getElementById("chatbot"),
  artboard: "chatbot",
  fit: rive.Fit.Cover,
  autoplay: true,
  stateMachines: "State Machine",
  // animations: ["blink"],
  onLoad: () => {
    r.setTextRunValue("message", "Hello");
    const inputs = r.stateMachineInputs("State Machine");

    // inputs.forEach((input) => {
    //   console.log(input.name); //print total inputs from stateMachine
    // });
    const isDefault = inputs.find((input) => input.name === "isDefault");
    const isListening = inputs.find((input) => input.name === "isListening");
    const isSpeaking = inputs.find((input) => input.name === "isSpeaking");
    const exitSpeaking = inputs.find((input) => input.name === "exitSpeaking");
    const isBlink = inputs.find((input) => input.name === "isBlink");
    const isHappy = inputs.find((input) => input.name === "isHappy");
    const isSad = inputs.find((input) => input.name === "isSad");
    const isError = inputs.find((input) => input.name === "isError");

    class riveBoolean {
      static setFalse() {
        isDefault.value = false;
        isListening.value = false;
        isSpeaking.value = false;
        isBlink.value = false;
        isHappy.value = false;
        isSad.value = false;
        isError.value = false;
      }
      static setTrue(name) {
        name.value = true;
      }
    }

    async function sendMessage() {
      window.speechSynthesis.cancel();
      const message = userInput.value.trim();
      if (!message) return;

      // Display user message
      addMessage("user", message);
      userInput.value = ""; // Clear the input field

      // Set the focus back to the input field for the next message
      userInput.focus();

      try {
        // Send message to the backend
        const response = await fetch("http://127.0.0.1:5000/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message }),
        });
        const data = await response.json();
        console.log(data);

        if (data.mode == "game") {
          riveBoolean.setFalse();
          riveBoolean.setTrue(isBlink);
          addMessage("PyChat", formatResponse(data.response));
          speakText(data);
          setTimeout(() => {
            gameBox.removeAttribute("hidden");
          }, 1000);
        } else if (data.mode == "code") {
          _currentIndex = 2;
          textModeBtn.classList.add("actived");
          voiceModeBtn.classList.remove("actived");
          chatbot.setAttribute("hidden", "true");
          chatbox.removeAttribute("hidden");
          recordBtn.setAttribute("hidden", "true");
          riveBoolean.setFalse();
          addMessage("PyChat", formatResponse(data.response));
        } else {
          addMessage("PyChat", formatResponse(data.response));
          speakText(data);
        }
      } catch (error) {
        addMessage("PyChat", "I'm having trouble connecting to the server.");
        r.setTextRunValue("message", "ERROR!");
        riveBoolean.setFalse();
        riveBoolean.setTrue(isError);
        setTimeout(() => {
          riveBoolean.setFalse();
        }, 2000);
      } finally {
        // Set loading state to false after the API call completes (success or failure)
        isLoading = false;
        console.log("API call completed.");
      }

      // Keep the chat scrolled to the bottom after each new message
      messages.scrollTop = messages.scrollHeight;
    }

    // Show the response in document
    function addMessage(sender, text) {
      const messageDiv = document.createElement("div");
      messageDiv.className = sender;

      if (sender === "user") {
        // Replace newline characters with <br> for line breaks in HTML
        messageDiv.innerHTML = text.replace(/\n/g, "<br>");
        messages.appendChild(messageDiv);
      } else {
        messageDiv.setAttribute("id", "typedtext");
        messages.appendChild(messageDiv);

        // Typewriter animation
        let aText = [text];
        let iSpeed = 80; // time delay of print out (adjust as needed)
        let sContents = "";
        let words = aText[0].split(" "); // Split text into words
        let iWordIndex = 0;

        function typewriter() {
          if (iWordIndex < words.length) {
            sContents += words[iWordIndex] + " ";
            messageDiv.innerHTML = sContents + "_"; // Cursor effect
            iWordIndex++;
            // Scroll to the bottom while typing
            messages.scrollTop = messages.scrollHeight;
            setTimeout(typewriter, iSpeed);
          } else {
            messageDiv.innerHTML = sContents; // Remove cursor when done
            // Scroll to the bottom once typing is done
            messages.scrollTop = messages.scrollHeight;
          }
        }

        setTimeout(typewriter, 1000);
      }
    }



    // Format response
    function formatResponse(response) {
      // Replace newline characters with <br> for line breaks in HTML
      return response.replace(/\n/g, "<br>");
    }

    userInput.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();  // Prevent the default "Enter" behavior (e.g., creating a new line)
        sendMessage();  // Call the sendMessage function when Enter is pressed
      }
    });


    // STT
    function speechRecognition() {
      window.speechSynthesis.cancel();
      const recognition = new (window.SpeechRecognition ||
        window.webkitSpeechRecognition)();
      recognition.lang = "en-US";
      //onStart
      recognition.onstart = () => {
        riveBoolean.setFalse();
        riveBoolean.setTrue(isListening);
        console.log("onStart");
      };
      //onEnd
      recognition.onend = () => {
        riveBoolean.setTrue(isDefault);
        console.log("onFinish");
        console.log(isListening.value);
      };
      //onResult
      recognition.onresult = (event) => {
        console.log("onResult");
        const speechResult = event.results[0][0].transcript.trim();
        if (speechResult) {
          riveBoolean.setTrue(isSpeaking);
          userInput.value = speechResult;
          sendMessage();
        } else {
          riveBoolean.setFalse();
          riveBoolean.setTrue(isDefault);
        }
      };
      //onError
      recognition.onerror = (e) => {
        console.log(e);
        r.setTextRunValue("message", "ERROR");
        riveBoolean.setFalse();
        riveBoolean.setTrue(isError);
        setTimeout(() => {
          riveBoolean.setFalse();
        }, 2000);
        addMessage(
          "PyChat",
          "Sorry, there was an issue with speech recognition."
        );
      };
      recognition.start();
    }

    //TTS
    function speakText(data) {

      const responseText = data.response;

      // Count the number of words in the response
      const wordCount = responseText.split(/\s+/).length;

      // Check if the word count exceeds 100
      if (wordCount > 250) {
        console.log("Response too long for speech synthesis.");
        return; // Skip speech synthesis if the response is too long
      }

      const utterance = new SpeechSynthesisUtterance(data.response);
      const voices = synth.getVoices();
      // utterance.voice =
      //   (voices.find((voice) => voice.name.includes("Female"))) ||
      //   voices[1];
      // Ensure text-to-speech speaks in a natural pace
      utterance.rate = 1;
      utterance.pitch = 1;
      //onStart
      utterance.onboundary = () => {
        console.log("Speech started");
        if (data.mode == "game" || data.mode == "blink") {
          riveBoolean.setFalse();
          riveBoolean.setTrue(isBlink);
        } else {
          riveBoolean.setTrue(isSpeaking);
        }
      };

      //onEnd
      utterance.onend = () => {
        window.currentUtterance = null; // Clear the reference
        if (data.mode == "happiness") {
          riveBoolean.setFalse();
          riveBoolean.setTrue(isHappy);
          setTimeout(() => {
            riveBoolean.setFalse();
          }, 2000);
        } else if (data.mode == "sadness") {
          riveBoolean.setFalse();
          riveBoolean.setTrue(isSad);
          setTimeout(() => {
            riveBoolean.setFalse();
          }, 2000);
        }
        // else if (data.mode == "table") {
        //   setTimeout(() => {
        //     blinkTable.setAttribute("hidden", "true");
        //     setTimeout(() => {
        //       riveBoolean.setFalse();
        //     }, 500);
        //   }, 3000);
        // }
        else if (data.mode == "game") {
        } else {
          riveBoolean.setFalse();
        }
        console.log("Speech finished");
      };
      synth.speak(utterance);
    }

    recordBtn.addEventListener("click", () => {
      speechRecognition();
    });
    sendBtn.addEventListener("click", () => {
      sendMessage();
    });
    exitBtn.addEventListener("click", () => {
      gameBox.setAttribute("hidden", "true");
      setTimeout(() => {
        riveBoolean.setFalse();
      }, 500);
    });
  },
});

function onMenuClicked(index) {
  if (index == 1) {
    _currentIndex = 1;
    voiceModeBtn.classList.add("actived");
    textModeBtn.classList.remove("actived");
    chatbox.setAttribute("hidden", "true");
    chatbot.removeAttribute("hidden");
    recordBtn.removeAttribute("hidden");
  } else {
    _currentIndex = 2;
    textModeBtn.classList.add("actived");
    voiceModeBtn.classList.remove("actived");
    chatbot.setAttribute("hidden", "true");
    chatbox.removeAttribute("hidden");
    recordBtn.setAttribute("hidden", "true");
  }
}

