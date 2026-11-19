$(document).ready(function () {
    // Initialize SiriWave Audio Visualizer
    if (document.getElementById("SiriWave")) {
        var siriWave = new SiriWave({
            container: document.getElementById("SiriWave"),
            width: 640,
            height: 100,
            style: "ios9",
            amplitude: 1,
            speed: 0.15,
            autostart: true
        });
    }

    // Handle Text Input Send Button Click
    $("#sendBtn").click(function () {
        let message = $("#textInput").val().trim();
        if (message !== "") {
            senderText(message);
            eel.process_command(message)();
            $("#textInput").val("");
        }
    });

    // Handle Enter Key Press in Input Box
    $("#textInput").keypress(function (e) {
        if (e.which == 13) {
            $("#sendBtn").click();
        }
    });

    // Handle Voice Microphone Button Click
    $("#micBtn").click(function () {
        eel.take_command()();
    });

    // Handle Stop Speech Button Click
    $("#stopBtn").click(function () {
        eel.stop_speaking()();
        $(".siri-message").text("Ask me anything");
    });

    // Run boot sequence when page loads
    runJarvisApp();
});

// Eel Exposed Functions (Called from Python Backend)
eel.expose(DisplayMessage);
function DisplayMessage(message) {
    $(".siri-message").text(message);
}

eel.expose(senderText);
function senderText(message) {
    var chatBox = $("#chat-canvas-body");
    if (chatBox.length) {
        chatBox.append(`
            <div class="d-flex justify-content-end mb-2">
                <div class="p-2 px-3 rounded-3" style="background: rgba(56, 189, 248, 0.2); border: 1px solid rgba(56, 189, 248, 0.3); max-width: 75%;">
                    <small class="text-info fw-bold d-block mb-1">You</small>
                    <span>${message}</span>
                </div>
            </div>
        `);
        chatBox.scrollTop(chatBox[0].scrollHeight);
    }
}

eel.expose(receiverText);
function receiverText(message) {
    $(".siri-message").text("Ask me anything");
    var chatBox = $("#chat-canvas-body");
    if (chatBox.length) {
        chatBox.append(`
            <div class="d-flex justify-content-start mb-2">
                <div class="p-2 px-3 rounded-3" style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(255, 255, 255, 0.1); max-width: 75%;">
                    <small class="fw-bold d-block mb-1" style="color: #38bdf8;">Jarvis</small>
                    <span>${message}</span>
                </div>
            </div>
        `);
        chatBox.scrollTop(chatBox[0].scrollHeight);
    }
}

// Automated Boot Sequence & Face Authentication Flow
async function runJarvisApp() {
    setTimeout(async function () {
        $("#Loader").attr("hidden", true);
        $("#FaceAuth").removeAttr("hidden");

        let authResult = await eel.face_auth()();

        if (authResult) {
            $("#FaceAuth").attr("hidden", true);
            $("#FaceAuthSuccess").removeAttr("hidden");

            setTimeout(function () {
                $("#FaceAuthSuccess").attr("hidden", true);
                $("#HelloGreet").removeAttr("hidden");

                setTimeout(function () {
                    $("#HelloGreet").attr("hidden", true);
                    $("#Start").removeAttr("hidden");

                    setTimeout(function () {
                        $("#Start").attr("hidden", true);
                        $("#Oval").removeAttr("hidden");
                    }, 1200);
                }, 1200);
            }, 1200);
        } else {
            alert("Face Authentication Failed or Cancelled. Please restart application.");
        }
    }, 1500);
}