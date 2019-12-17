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
          <button class="Polaris-Button" @click="refreshSeating">REFRESH SEATING</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { filterMy, filterAll } from '../constants';
import { adminEmails } from '../../../config';

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
    };
  },
  computed: {
    isAdminEmail() {
      return adminEmails.includes(this.email);
    },
    userHasChannel() {
      return this.userChannel !== 'no_channel';
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
    refreshSeating() {
      this.$root.$emit('refreshSeating');
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
