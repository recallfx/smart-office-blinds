import firebase from '@firebase/app';
import '@firebase/auth';
import '@firebase/firestore';
import '@firebase/functions';

import Vue from 'vue/dist/vue.esm.browser';
import App from './components/app.vue';

new Vue({
    el: '#app',
    components: {
        App,
    },
    data: {
        firebaseConfig: {
            apiKey: "AIzaSyDd-E2W1A2Pxh5B6Njiv4QByAZ3-eb1rgg",
            authDomain: "sob-mbieliau-firebase-2d798.firebaseapp.com",
            databaseURL: "https://sob-mbieliau-firebase-2d798.firebaseio.com",
            projectId: "sob-mbieliau-firebase-2d798",
            storageBucket: "sob-mbieliau-firebase-2d798.appspot.com",
            messagingSenderId: "308296092122",
            appId: "1:308296092122:web:68705d4988c4c2c2a498e3"
        },
        allowedDomain: 'shopify.com',
        initialising: true,
        firebase: null,
        firebaseLoaded: false,
        errorMessage: null,
        user: null,
        channels: [],
        commands: [],
    },
    methods: {
        logException(ex) {
            this.$set(this, 'errorMessage', ex);
            console.error(ex);
        },

        clearException() {
            if (this.errorMessage) {
                this.$set(this, 'errorMessage', null);
            }
        },

        logMessage(message) {
            console.log(message);
        },

        initFirebase() {
            try {
                this.firebase = firebase.initializeApp(this.firebaseConfig);

                // https://support.google.com/firebase/answer/7015592
                const isProduction = window.location.hostname !== 'localhost';
                const functionsEmulatorUrl = 'http://localhost:5001';

                if (!isProduction) {
                    this.firebase.functions().useFunctionsEmulator(functionsEmulatorUrl)
                }

                this.$set(this, 'firebaseLoaded', true);
            } catch (e) {
                this.logException(e);
            }
        },

        initAuth() {
            try {
                this.firebase.auth().onAuthStateChanged((user) => {
                    if (this.initialising) {
                        this.$set(this, 'initialising', false);
                    }

                    if (user) {
                        this.userSignedIn(user);
                        this.initDatabase();
                    } else {
                        this.userSignedOut();
                        this.stopFollowing()
                    }
                });
            } catch (e) {
                this.logException(e);
            }
        },

        userSignedIn(user) {
            const {
                displayName,
                email,
                emailVerified,
                photoURL,
                isAnonymous,
                uid,
                providerData,
            } = user;

            this.$set(this, 'user', {
                displayName,
                email,
                emailVerified,
                photoURL,
                isAnonymous,
                uid,
                providerData,
            });
        },

        userSignedOut() {
            this.$set(this, 'user', null);
        },

        async initDatabase() {
            try {
                const channels = [];
                const querySnapshot = await this.firebase.firestore().collection("channels").get();                

                querySnapshot.forEach((doc) => {
                    channels.push(doc.data());
                });

                this.$set(this, 'channels', channels);
            } catch (e) {
                this.logException(e);
            }
        },

        updateChannel(channel) {
            const index = this.channels.findIndex((vueChannel) => vueChannel.name === channel.name);

            if (index > 0) {
                this.$set(this.channels, index, channel);
            }
        },

        updateCommands(commands) {
            this.logMessage('commands', commands);
            this.$set(this, 'commands', commands);
        },

        subscribe(channelName) {
            if (!this.unsubscribeChannelCb) {
                const channelRef = this.firebase.firestore().collection("channels").doc(channelName);

                this.unsubscribeChannelCb = channelRef
                    .onSnapshot((channelDoc) => {
                        this.updateChannel(channelDoc.data());
                    }, (error) => {
                        this.logException(error);
                    });
            }

            if (!this.unsubscribeCommandsCb) {
                const commandsRef = this.firebase.firestore().collection("commands").orderBy("timestamp", "desc").limit(1);

                this.unsubscribeCommandsCb = commandsRef
                    .onSnapshot((querySnapshot) => {
                        const commands = [];

                        querySnapshot.forEach((doc) => {
                            commands.push(doc.data());
                        });

                        this.updateCommands(commands);
                    }, (error) => {
                        this.logException(error);
                    });
            }
        },

        unsubscribe() {
            if (this.unsubscribeChannelCb) {
                this.unsubscribeChannelCb();
                this.unsubscribeChannelCb = null;
            }

            if (this.unsubscribeCommandsCb) {
                this.unsubscribeCommandsCb();
                this.unsubscribeCommandsCb = null;
            }
        },

        // actions?
        async signOut() {
            if (!this.firebase) {
                return;
            }

            try {
                await this.firebase.auth().signOut();
            } catch (e) {
                this.logException(e);
            }
        },

        async setPersistence() {
            try {
                await this.firebase.auth().setPersistence(firebase.auth.Auth.Persistence.LOCAL);
            } catch (error) {
                this.logException(error);
            }
        },

        async signIn() {
            const provider = new firebase.auth.GoogleAuthProvider();
            provider.addScope('openid');
            provider.addScope('profile');
            provider.addScope('email');

            try {
                await this.firebase.auth().signInWithPopup(provider);
            } catch (e) {
                this.logException(e);
            }
        },

        async command(channel, action) {
            const setCommand = this.firebase.functions().httpsCallable('setCommand');

            try {
                const result = await setCommand({ channel, action });

                if (result.data && result.data.code !== 200) {
                    this.logException(result.data.message.details);                        
                } else {
                    this.logMessage(result);
                }
            } catch (error) {
                this.logException(error);
            }
        },
    },

    mounted() {
        this.initFirebase();

        if (this.firebase) {
            this.initAuth();
        }

        // for simplicity, events are emitted from $root within components
        this.$on('login', () => {
            this.clearException();
            this.setPersistence();
            this.signIn();
        });

        this.$on('logout', () => {
            this.clearException();
            this.signOut();
        });

        this.$on('command', (channel, action) => {
            this.clearException();
            this.command(channel, action);
        });

        this.$on('subscribe', (channelName) => {
            this.subscribe(channelName);
        });

        this.$on('unsubscribe', (channelName) => {
            this.unsubscribe(channelName);
        });
    },
});
