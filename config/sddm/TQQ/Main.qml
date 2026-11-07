import QtQuick 2.12
import QtQuick.Controls 2.5
import QtQuick.Layouts 1.12

Rectangle {
    id: root
    width: 1920
    height: 1080
    color: "#111323"
    focus: true

    property string currentTime: ""
    property string currentDate: ""
    property string loginMessage: ""
    property bool submitting: false

    function updateClock() {
        var now = new Date()
        currentTime = Qt.formatTime(now, "hh\nmm")
        currentDate = Qt.formatDate(now, "dddd, d MMMM")
    }

    function submitLogin() {
        if (username.text.length === 0 || password.text.length === 0) {
            loginMessage = "Enter your username and password"
            return
        }
        submitting = true
        loginMessage = "Signing in…"
        sddm.login(username.text, password.text, sessionPicker.currentIndex)
    }

    Image {
        id: wallpaper
        anchors.fill: parent
        source: "background.jpeg"
        fillMode: Image.PreserveAspectCrop
        asynchronous: true
        smooth: true
        transformOrigin: Item.Center
        scale: 1.04

        SequentialAnimation on scale {
            loops: Animation.Infinite
            running: true
            NumberAnimation { to: 1.095; duration: 70000; easing.type: Easing.InOutSine }
            NumberAnimation { to: 1.04; duration: 70000; easing.type: Easing.InOutSine }
        }
    }

    Rectangle {
        anchors.fill: parent
        color: "#15152a"
        opacity: 0.34
    }

    Rectangle {
        id: frame
        width: Math.min(parent.width * 0.84, 1460)
        height: Math.min(parent.height * 0.84, 940)
        anchors.centerIn: parent
        radius: 28
        color: "#10131d"
        opacity: 0.76
        border.width: 1
        border.color: "#8f9ab8"

        Rectangle {
            anchors.fill: parent
            anchors.margins: 1
            radius: parent.radius
            color: "transparent"
            border.width: 1
            border.color: "#35ffffff"
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: Math.max(28, frame.width * 0.065)
            spacing: 0

            RowLayout {
                Layout.fillWidth: true

                Text {
                    text: root.currentDate
                    color: "#d8d9e8"
                    font.pixelSize: Math.max(13, frame.width * 0.012)
                    font.letterSpacing: 1.2
                    opacity: 0.88
                }

                Item { Layout.fillWidth: true }

                ComboBox {
                    id: sessionPicker
                    model: sessionModel
                    textRole: "name"
                    currentIndex: sessionModel.lastIndex
                    implicitWidth: Math.max(150, frame.width * 0.16)
                    implicitHeight: 42
                    font.pixelSize: 14
                    opacity: 0.92

                    background: Rectangle {
                        radius: 12
                        color: "#302d3b"
                        border.color: "#50ffffff"
                    }
                    contentItem: Text {
                        leftPadding: 14
                        rightPadding: 34
                        text: sessionPicker.displayText
                        color: "#f3f0f7"
                        font: sessionPicker.font
                        verticalAlignment: Text.AlignVCenter
                        elide: Text.ElideRight
                    }
                }
            }

            Item { Layout.fillHeight: true }

            Text {
                Layout.alignment: Qt.AlignHCenter
                text: root.currentTime
                color: "#f2f1dd"
                font.family: "Noto Sans"
                font.pixelSize: Math.min(frame.width * 0.125, frame.height * 0.19)
                font.weight: Font.Light
                lineHeight: 0.83
                lineHeightMode: Text.ProportionalHeight
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                style: Text.Raised
                styleColor: "#3010131d"
            }

            Item { Layout.fillHeight: true }

            ColumnLayout {
                Layout.alignment: Qt.AlignHCenter
                Layout.preferredWidth: Math.min(frame.width * 0.42, 430)
                spacing: 12

                TextField {
                    id: username
                    Layout.fillWidth: true
                    Layout.preferredHeight: 52
                    text: userModel.lastUser
                    placeholderText: "Username"
                    color: "#f4f1f7"
                    placeholderTextColor: "#a8a6b3"
                    font.pixelSize: 16
                    leftPadding: 18
                    selectByMouse: true
                    background: Rectangle {
                        radius: 13
                        color: "#40272a38"
                        border.color: username.activeFocus ? "#d8acd9" : "#50ffffff"
                    }
                    onAccepted: password.forceActiveFocus()
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    TextField {
                        id: password
                        Layout.fillWidth: true
                        Layout.preferredHeight: 52
                        placeholderText: "Password"
                        echoMode: TextInput.Password
                        color: "#f4f1f7"
                        placeholderTextColor: "#a8a6b3"
                        font.pixelSize: 16
                        leftPadding: 18
                        selectByMouse: true
                        background: Rectangle {
                            radius: 13
                            color: "#40272a38"
                            border.color: password.activeFocus ? "#d8acd9" : "#50ffffff"
                        }
                        onAccepted: root.submitLogin()
                    }

                    Button {
                        id: loginButton
                        Layout.preferredWidth: 56
                        Layout.preferredHeight: 52
                        enabled: !root.submitting
                        onClicked: root.submitLogin()
                        contentItem: Text {
                            text: "→"
                            color: "#171725"
                            font.pixelSize: 27
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        background: Rectangle {
                            radius: 13
                            color: loginButton.enabled ? "#d7badb" : "#93849a"
                        }
                    }
                }

                Text {
                    Layout.fillWidth: true
                    text: root.loginMessage
                    color: "#f1c1d2"
                    font.pixelSize: 13
                    horizontalAlignment: Text.AlignHCenter
                    visible: text.length > 0
                }
            }

            Item { Layout.preferredHeight: 20 }

            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "THE QUINTESSENTIAL QUINTUPLETS"
                color: "#bfc0cf"
                font.pixelSize: 10
                font.letterSpacing: 3
                opacity: 0.72
            }
        }
    }

    Timer {
        interval: 1000
        repeat: true
        running: true
        triggeredOnStart: true
        onTriggered: root.updateClock()
    }

    NumberAnimation {
        target: frame
        property: "opacity"
        from: 0
        to: 1
        duration: 1100
        easing.type: Easing.OutCubic
        running: true
    }

    NumberAnimation {
        target: frame
        property: "scale"
        from: 0.985
        to: 1
        duration: 1300
        easing.type: Easing.OutCubic
        running: true
    }

    Connections {
        target: sddm
        function onLoginFailed() {
            root.submitting = false
            root.loginMessage = "Login failed. Check your username and password."
            password.text = ""
            password.forceActiveFocus()
        }
        function onLoginSucceeded() {
            root.loginMessage = "Welcome"
        }
    }

    Component.onCompleted: {
        updateClock()
        if (username.text.length === 0)
            username.forceActiveFocus()
        else
            password.forceActiveFocus()
    }
}
