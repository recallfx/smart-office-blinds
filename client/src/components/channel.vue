<template>
  <div class="Polaris-Card__Section">
    <div class="Polaris-Card__SectionHeader">

      <div class="Polaris-Stack Polaris-Stack--alignmentCenter">
        <div class="Polaris-Stack__Item">
          <h3 class="Polaris-Subheading">{{label}}</h3>
        </div>
        <div class="Polaris-Stack__Item">
          <span class="Polaris-Badge Polaris-Badge--statusInfo"><span class="Polaris-VisuallyHidden">Info</span><span class="Polaris-Badge__Content">{{ capitalizedStatus }}</span></span>
        </div>
      </div>
    </div>

    <div class="Polaris-ButtonGroup Polaris-ButtonGroup--segmented" data-buttongroup-segmented="true">
      <action
        v-for="action in availableActions"
        :key="action"
        :channel-name="name"
        :action="action"
        :disabled="disabled"
        @command="onCommand"
      />
    </div>

    <commands :commands="channelCommands" />
  </div>
</template>

<script>
import Action from "./action.vue";
import Commands from "./commands.vue";
import {capitalize} from '../utils';

const IDLE = 'idle';
const SENDING_REQUEST = 'sending request';
const WORKING = 'working';

let timeoutId = null;
const MAX_WORKING_TIMEOUT = 120000;

export default {
  components: {
    Action,
    Commands,
  },
  props: {
    name: String,
    label: String,
    availableActions: Array,
    lastAction: String,
    status: String,
    commands: Array,
    hasCorrectDomain: Boolean,
  },
  data() {
    return {
      localStatus: IDLE,
    };
  },
  computed: {
    disabled() {
      return !this.hasCorrectDomain || this.localStatus !== IDLE;
    },
    capitalizedStatus() {
      return capitalize(this.localStatus);
    },

    channelCommands() {
      return this.commands.filter((command) => command.channel === this.name);
    },
  },

  watch: {
    status(newStatus, oldStatus) {
      this.$set(this, 'localStatus', newStatus);
    },

    localStatus(newLocalStatus, oldLocalStatus) {
      if (newLocalStatus !== oldLocalStatus) {
        if (newLocalStatus !== IDLE) {
          // start timer
          timeoutId = setTimeout(() => {
            this.$set(this, 'localStatus', IDLE);
          }, MAX_WORKING_TIMEOUT)
        } else {
          // stop timer
          clearTimeout(timeoutId)
        }
      }
    },
  },

  methods: {
    onCommand(channelName, action) {
      this.$set(this, 'localStatus', SENDING_REQUEST);

      this.$root.$emit('command', channelName, action, (error) => {
        if (error) {
          this.$set(this, 'localStatus', IDLE);
        }
      });
    },
  },
};
</script>
