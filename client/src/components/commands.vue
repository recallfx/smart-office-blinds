<template>
    <ul v-if="commands.length > 0" class="commands">
        <li v-for="command in commands" :key="timestamp(command.timestamp)">
            <div class="Polaris-Stack">
                <div class="Polaris-Stack__Item">{{timestampToLocaleString(command.timestamp)}}</div>
                <div class="Polaris-Stack__Item">{{userName(command.email)}}</div>
                <div class="Polaris-Stack__Item"><span class="Polaris-Badge"><span class="Polaris-Badge__Content">{{actionName(command.action)}}</span></span></div>
            </div>
        </li>
    </ul>
</template>

<script>
import {capitalize} from '../utils';
import moment from 'moment';

export default {
  props: {
    commands: Array,
  },
  methods: {
      timestampToLocaleString(timestamp) {
        return moment(timestamp.toDate()).fromNow();
      },
      timestamp(timestamp) {
        return timestamp.toDate().getTime();
      },
      userName(email) {
        return email.split('@')[0].split('.').map(s => capitalize(s)).join(' ');
      },
      actionName(action) {
        return action.split('_').map(s => capitalize(s)).join(' ');
      },
  },
}
</script>
