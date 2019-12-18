<template>
  <div class="Polaris-Layout__Section">
    <div class="Polaris-Card">
      <div class="Polaris-Card__Section">
        <div class="Polaris-Stack">
          <div v-if="email" class="Polaris-Stack__Item">
            <span class="Polaris-Badge" :class="{'Polaris-Badge--statusSuccess': hasCorrectDomain, 'Polaris-Badge--statusWarning': !hasCorrectDomain}">
              <span class="Polaris-VisuallyHidden">Email</span>
              {{email}}
            </span>
          </div>
          <div v-if="userHasChannel" class="Polaris-Stack__Item">
            <input :id="filterMy" type="radio" class="hidden" name="filter" value="my" @input="onInput(filterMy)">
            <label :for="filterMy" :class="{ active: filter === filterMy }">My channel</label>
          </div>
          <div class="Polaris-Stack__Item">
            <input :id="filterAll" type="radio" class="hidden" name="filter" value="all" @input="onInput(filterAll)">
            <label :for="filterAll" :class="{ active: filter === filterAll }">All channels</label>
          </div>
          <div class="Polaris-Stack__Item">
            <a v-if="isLoggedIn" class="Polaris-Link" href="#" @click="onLogoutClick">Logout</a>
            <a v-if="!isLoggedIn" class="Polaris-Link" href="#" @click="onLoginClick">Login</a>
          </div>
        </div>
        <div class="adminButton" v-if="isLoggedIn && isAdminEmail">
            <div class="Polaris-ButtonGroup__Item">
              <button
                type="button"
                class="Polaris-Button"
                :class="{'Polaris-Button--disabled': loading }"
                :disabled="loading"
                @click="onRefreshSeating"
              >
                <span class="Polaris-Button__Content">
                  <span class="Polaris-Button__Text">Refresh Seating</span>
                </span>
              </button>
            </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { filterMy, filterAll } from '../../../constants';
import { adminEmails } from '../../../config.json';

export default {
  props: {
    isLoggedIn: Boolean,
    hasCorrectDomain: Boolean,
    email: String,
    updateFilter: Function,
    filter: String,
    userChannel: String,
  },
  data() {
    return {
      filterAll,
      filterMy,
      loading: false,
    };
  },
  computed: {
    isAdminEmail() {
      return adminEmails.includes(this.email);
    },
    userHasChannel() {
      return this.userChannel;
    },
  },
  methods: {
    onLoginClick() {
      this.$root.$emit('login');
    },
    onLogoutClick() {
      this.$root.$emit('logout');
    },
    onInput(value) {
      this.$emit('updateFilter', value);
    },
    onRefreshSeating() {
      this.$set(this, 'loading', true);
      this.$root.$emit('refreshSeating', () => {
        this.$set(this, 'loading', false);
      });
    },
  },
}
</script>
<style>
  .hidden {
    display: none;
  }

  .active {
    font-weight: bold;
  }

  .adminButton {
    margin-top: 20px;
  }
</style>
