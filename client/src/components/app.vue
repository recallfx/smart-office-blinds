<template>
  <div class="Polaris-Page">
    <div class="Polaris-Page-Header Polaris-Page-Header--hasNavigation Polaris-Page-Header--hasActionMenu">
      <div class="Polaris-Page-Header__MainContent">
        <div class="Polaris-Page-Header__TitleActionMenuWrapper">
          <div class="Polaris-Page-Header__Title">
            <div>
              <h1 class="Polaris-DisplayText Polaris-DisplayText--sizeLarge">Smart office blinds</h1>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="Polaris-Page__Content">
      <div class="Polaris-Layout">

        <error-banner title="Error" :error="errorMessage" />

        <div v-if="initialising" class="Polaris-Layout__Section" style="text-align: center;">
          <img src="data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgNDQgNDQiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTE1LjU0MiAxLjQ4N0EyMS41MDcgMjEuNTA3IDAgMDAuNSAyMmMwIDExLjg3NCA5LjYyNiAyMS41IDIxLjUgMjEuNSA5Ljg0NyAwIDE4LjM2NC02LjY3NSAyMC44MDktMTYuMDcyYTEuNSAxLjUgMCAwMC0yLjkwNC0uNzU2QzM3LjgwMyAzNC43NTUgMzAuNDczIDQwLjUgMjIgNDAuNSAxMS43ODMgNDAuNSAzLjUgMzIuMjE3IDMuNSAyMmMwLTguMTM3IDUuMy0xNS4yNDcgMTIuOTQyLTE3LjY1YTEuNSAxLjUgMCAxMC0uOS0yLjg2M3oiIGZpbGw9IiM5MTlFQUIiLz48L3N2Zz4K" alt="" class="Polaris-Spinner Polaris-Spinner--colorTeal Polaris-Spinner--sizeLarge" draggable="false"><span role="status"><span class="Polaris-VisuallyHidden">Spinner example</span></span>
        </div>

        <template v-if="!initialising">
          <error-banner title="Wrong domain" :error="wrongDomainError" />

          <user-section
            :email="userEmail"
            :is-logged-in="isLoggedIn"
            :filter="filter"
            :has-correct-domain="hasCorrectDomain"
            @updateFilter="updateFilter"
            :user-channel="userChannel"
          />
          <channels v-if="isLoggedIn" :channels="channelsToShow" :has-correct-domain="hasCorrectDomain" :commands="commands" />
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import UserSection from './user-section.vue';
import Channels from './channels.vue';
import ErrorBanner from './error-banner.vue';
import { filterAll, filterMy } from '../../../constants';
import {hasAllowedDomain} from '../utils';

export default {
  props: {
      initialising: Boolean,
      allowedDomains: Array,
      firebaseLoaded: Boolean,
      errorMessage: Error,
      user: Object,
      channels: Array,
      commands: Array,
      userChannel: String,
  },
  data() {
      return {
          filter: filterAll,
      };
  },
  components: {
    UserSection,
    Channels,
    ErrorBanner,
  },
  methods: {
    updateFilter(value) {
      this.$set(this, 'filter', value);
    },
  },
  watch: {
    userChannel: function(newChannel) {
        this.$set(this, 'filter', newChannel === 'no_channel'? filterAll : filterMy )
    },
  },
  computed: {
    channelsToShow() {
        if (this.filter === filterMy) {
            return this.channels.filter(c => c.name === this.userChannel);
        }

        return this.channels;
    },
    isLoggedIn() {
      return this.user !== null;
    },
    userEmail() {
      if (this.isLoggedIn) {
        return this.user.email;
      }

      return null;
    },
    hasCorrectDomain() {
      return hasAllowedDomain(this.userEmail, this.allowedDomains);
    },
    wrongDomainError() {
      if (this.isLoggedIn && !this.hasCorrectDomain) {
        return 'Your email domain is unsupported';
      }

      return null;
    }
  },
};
</script>
