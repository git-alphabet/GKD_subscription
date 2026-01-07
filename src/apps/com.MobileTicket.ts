import { defineGkdApp } from '@gkd-kit/define';

export default defineGkdApp({
  id: 'com.MobileTicket',
  name: '铁路12306',
  groups: [
    {
      key: 0,
      name: '开屏广告',
      matchTime: 10000,
      actionMaximum: 1,
      resetMatch: 'app',
      priorityTime: 10000,
      rules: [
        {
          fastQuery: true,
          matches:
            '[vid="tv_main_splash_skip" || vid="tv_skip"][visibleToUser=true]',
          exampleUrls: 'https://e.gkd.li/9a9b71b2-0c52-4623-b53b-6dd07d0cbe7c',
          snapshotUrls: [
            'https://i.gkd.li/i/17580273',
            'https://i.gkd.li/i/17656103',
          ],
        },
      ],
    },
    // 这里是新添加的规则，key 不能重复，所以设为 1
    {
      key: 1,
      name: '首页-通知权限弹窗',
      desc: '自动点击关闭',
      fastQuery: true,
      matchTime: 10000,
      actionMaximum: 1,
      resetMatch: 'app',
      rules: [
        {
          activityIds: 'com.MobileTicket.ui.activity.MainActivity',
          matches: 'ImageView[desc="关闭"]',
          snapshotUrls: 'https://i.gkd.li/i/24474930',
        },
      ],
    },
  ],
});
