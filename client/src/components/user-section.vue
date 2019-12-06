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
          <div class="Polaris-Stack__Item">
            <a v-if="isLoggedIn" class="Polaris-Link" href="#" @click="onLogoutClick">Logout</a>
            <a v-if="!isLoggedIn" class="Polaris-Link" href="#" @click="onLoginClick">Login</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    isLoggedIn: Boolean,
    hasCorrectDomain: Boolean,
    email: String,
  },
  methods: {
    onLoginClick() {
      this.$root.$emit('login');
    },
    onLogoutClick() {
      this.$root.$emit('logout');
    },
  },
}
</script>