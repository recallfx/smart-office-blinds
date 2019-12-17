import firebase from '@firebase/app';
import '@firebase/auth';
import '@firebase/firestore';
import '@firebase/functions';
import { firebaseConfig, allowedDomains } from '../../config.json';
import { databaseCollections, dataCollectionDocuments } from '../../constants';
import Vue from 'vue/dist/vue.esm.browser';
import App from './components/app.vue';

new Vue({
  el: '#app',
  components: {
    App,
  },
  data: {
    firebaseConfig,
    allowedDomains,
    initialising: true,
    firebaseApp: null,
    firebaseLoaded: false,
    errorMessage: null,
    user: null,
    channels: [],
    commands: [],
    userChannel: null,
  },
  mounted() {
    this.initFirebase();

    if (this.firebaseApp) {
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

    this.$on('subscribe', channelName => {
      this.subscribe(channelName);
    });

    this.$on('unsubscribe', channelName => {
      this.unsubscribe(channelName);
    });

    this.$on('refreshSeating', () => {
      this.refreshSeating();
    });
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
        this.firebaseApp = firebase.initializeApp(this.firebaseConfig);

        // https://support.google.com/firebase/answer/7015592
        const isProduction = window.location.hostname !== 'localhost';
        const functionsEmulatorUrl = 'http://localhost:5001';

        if (!isProduction) {
          this.firebaseApp.functions().useFunctionsEmulator(functionsEmulatorUrl);
        }

        this.$set(this, 'firebaseLoaded', true);
      } catch (e) {
        this.logException(e);
      }
    },

    initAuth() {
      try {
        this.firebaseApp.auth().onAuthStateChanged(user => {
          if (this.initialising) {
            this.$set(this, 'initialising', false);
          }

          if (user) {
            this.userSignedIn(user);
            this.setChannel();
            this.initDatabase();
          } else {
            this.userSignedOut();
          }
        });
      } catch (e) {
        this.logException(e);
      }
    },

    async setChannel() {
      const docRef = this.firebaseApp
        .firestore()
        .collection(databaseCollections.data)
        .doc(dataCollectionDocuments.users);

      let doc = null;
      let channelName = null;

      try {
        doc = await docRef.get();
      } catch (error) {
        this.logException(error);
      }

      if (doc && doc.exists) {
        const mappedUsers = doc.data().mappedUsers;

        if (mappedUsers) {
          const user = mappedUsers.find(user => user.email === this.user.email);

          if (user) {
            channelName = user.channelName;
          } else {
            this.logMessage(`User ${this.user.email} not found in database!`);
          }
        }
      } else {
        this.logMessage('No user data in database!');
      }

      this.$set(this, 'userChannel', channelName);
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
        const querySnapshot = await this.firebaseApp
          .firestore()
          .collection(databaseCollections.channels)
          .get();

        querySnapshot.forEach(doc => {
          channels.push(doc.data());
        });

        this.$set(this, 'channels', channels);
      } catch (e) {
        this.logException(e);
      }
    },

    updateChannel(channel) {
      const index = this.channels.findIndex(
        vueChannel => vueChannel.name === channel.name
      );

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
        const channelRef = this.firebaseApp
          .firestore()
          .collection(databaseCollections.channels)
          .doc(channelName);

        this.unsubscribeChannelCb = channelRef.onSnapshot(
          channelDoc => {
            this.updateChannel(channelDoc.data());
          },
          error => {
            this.logException(error);
          }
        );
      }

      if (!this.unsubscribeCommandsCb) {
        const commandsRef = this.firebaseApp
          .firestore()
          .collection(databaseCollections.commands)
          .orderBy('timestamp', 'desc')
          .limit(1);

        this.unsubscribeCommandsCb = commandsRef.onSnapshot(
          querySnapshot => {
            const commands = [];

            querySnapshot.forEach(doc => {
              commands.push(doc.data());
            });

            this.updateCommands(commands);
          },
          error => {
            this.logException(error);
          }
        );
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
      if (!this.firebaseApp) {
        return;
      }

      try {
        await this.firebaseApp.auth().signOut();
      } catch (e) {
        this.logException(e);
      }
    },

    async setPersistence() {
      try {
        await this.firebaseApp
          .auth()
          .setPersistence(firebase.auth.Auth.Persistence.LOCAL);
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
        await this.firebaseApp.auth().signInWithPopup(provider);
      } catch (e) {
        this.logException(e);
      }
    },

    async command(channel, action) {
      const setCommand = this.firebaseApp.functions().httpsCallable('setCommand');

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

    async refreshSeating() {
      const refreshSeating = this.firebaseApp
        .functions()
        .httpsCallable('refreshSeating');

      try {
        const result = await refreshSeating();

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
});
