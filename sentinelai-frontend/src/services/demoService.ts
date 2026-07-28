import api from './api';

const SAMPLE_LOGS: Array<{ filename: string; source: string; content: string }> = [
  {
    filename: 'apache-access.log',
    source: 'apache',
    content: `192.168.1.100 - admin [10/Jul/2024:08:12:34 +0000] "GET /admin/login.php HTTP/1.1" 200 5321 "-" "Mozilla/5.0"
10.0.0.50 - - [10/Jul/2024:08:13:01 +0000] "POST /wp-admin/admin-ajax.php HTTP/1.1" 403 234 "-" "python-requests/2.31"
192.168.1.100 - admin [10/Jul/2024:08:14:22 +0000] "POST /api/v1/auth/login HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
203.0.113.5 - - [10/Jul/2024:08:15:00 +0000] "GET /wp-login.php HTTP/1.1" 200 5432 "-" "Mozilla/5.0"
203.0.113.5 - - [10/Jul/2024:08:15:01 +0000] "POST /wp-login.php HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
203.0.113.5 - - [10/Jul/2024:08:15:02 +0000] "POST /wp-login.php HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
203.0.113.5 - - [10/Jul/2024:08:15:03 +0000] "POST /wp-login.php HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
203.0.113.5 - - [10/Jul/2024:08:15:04 +0000] "POST /wp-login.php HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
203.0.113.5 - - [10/Jul/2024:08:15:05 +0000] "POST /wp-login.php HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
198.51.100.20 - - [10/Jul/2024:08:20:00 +0000] "GET /shell.php?cmd=whoami HTTP/1.1" 404 123 "-" "curl/8.0"
198.51.100.20 - - [10/Jul/2024:08:20:01 +0000] "GET /evil.php?cmd=id HTTP/1.1" 404 123 "-" "curl/8.0"
10.0.0.50 - - [10/Jul/2024:08:25:00 +0000] "GET /index.php?option=com_content&view=article&id=1 HTTP/1.1" 200 2345 "-" "Mozilla/5.0"
10.0.0.50 - - [10/Jul/2024:08:25:01 +0000] "POST /index.php?option=com_users&view=registration HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
192.168.1.100 - admin [10/Jul/2024:08:30:00 +0000] "GET /dashboard HTTP/1.1" 200 4321 "-" "Mozilla/5.0"
192.168.1.100 - admin [10/Jul/2024:08:30:05 +0000] "GET /api/v1/dashboard/summary HTTP/1.1" 200 123 "-" "Mozilla/5.0"`,
  },
  {
    filename: 'auth.log',
    source: 'linux',
    content: `Jul 10 08:11:15 webserv sshd[1234]: Accepted publickey for admin from 192.168.1.100 port 54321 ssh2: RSA SHA256:abc123
Jul 10 08:12:30 webserv sshd[1235]: Failed password for root from 203.0.113.5 port 39322 ssh2
Jul 10 08:12:31 webserv sshd[1236]: Failed password for root from 203.0.113.5 port 39323 ssh2
Jul 10 08:12:32 webserv sshd[1237]: Failed password for root from 203.0.113.5 port 39324 ssh2
Jul 10 08:12:33 webserv sshd[1238]: Failed password for root from 203.0.113.5 port 39325 ssh2
Jul 10 08:12:34 webserv sshd[1239]: Failed password for root from 203.0.113.5 port 39326 ssh2
Jul 10 08:12:35 webserv sshd[1240]: Failed password for root from 203.0.113.5 port 39327 ssh2
Jul 10 08:12:36 webserv sshd[1241]: Failed password for root from 203.0.113.5 port 39328 ssh2
Jul 10 08:12:37 webserv sshd[1242]: Failed password for root from 203.0.113.5 port 39329 ssh2
Jul 10 08:12:38 webserv sshd[1243]: Failed password for root from 203.0.113.5 port 39330 ssh2
Jul 10 08:13:00 webserv sshd[1244]: Failed password for invalid user admin from 203.0.113.5 port 39331 ssh2
Jul 10 08:14:00 webserv sudo:    admin : TTY=pts/0 ; PWD=/home/admin ; USER=root ; COMMAND=/bin/su -
Jul 10 08:15:00 webserv sshd[1245]: Accepted password for admin from 192.168.1.100 port 54322 ssh2
Jul 10 08:20:00 webserv sshd[1246]: Failed password for www-data from 198.51.100.20 port 44321 ssh2
Jul 10 08:20:01 webserv sshd[1247]: Failed password for www-data from 198.51.100.20 port 44322 ssh2
Jul 10 08:25:00 webserv sshd[1248]: Connection closed by authenticating user root 203.0.113.5 port 39332 [preauth]`,
  },
  {
    filename: 'nginx-access.log',
    source: 'nginx',
    content: `192.168.1.100 - - [10/Jul/2024:08:11:00 +0000] "GET / HTTP/1.1" 200 1234 "-" "Mozilla/5.0" "-"
10.0.0.50 - - [10/Jul/2024:08:12:00 +0000] "GET /wp-admin HTTP/1.1" 301 162 "-" "python-requests/2.31" "-"
203.0.113.5 - - [10/Jul/2024:08:13:00 +0000] "GET /xmlrpc.php HTTP/1.1" 200 432 "-" "Mozilla/5.0" "-"
203.0.113.5 - - [10/Jul/2024:08:13:01 +0000] "POST /xmlrpc.php HTTP/1.1" 200 567 "-" "Mozilla/5.0" "-"
203.0.113.5 - - [10/Jul/2024:08:13:02 +0000] "POST /xmlrpc.php HTTP/1.1" 200 567 "-" "Mozilla/5.0" "-"
203.0.113.5 - - [10/Jul/2024:08:13:03 +0000] "POST /xmlrpc.php HTTP/1.1" 200 567 "-" "Mozilla/5.0" "-"
203.0.113.5 - - [10/Jul/2024:08:13:04 +0000] "POST /xmlrpc.php HTTP/1.1" 200 567 "-" "Mozilla/5.0" "-"
198.51.100.20 - - [10/Jul/2024:08:20:00 +0000] "GET /admin/phpinfo.php HTTP/1.1" 404 123 "-" "curl/8.0" "-"
192.168.1.100 - admin [10/Jul/2024:08:30:00 +0000] "GET /api/v1/health HTTP/1.1" 200 45 "-" "Mozilla/5.0" "-"
192.168.1.100 - admin [10/Jul/2024:08:30:01 +0000] "GET /dashboard HTTP/1.1" 200 5432 "-" "Mozilla/5.0" "-"`,
  },
];

function fileToBlob(content: string, filename: string): File {
  return new File([content], filename, { type: 'text/plain' });
}

export const demoService = {
  async seedDemoData(): Promise<{ uploaded: number; parsed: number }> {
    let uploaded = 0;
    let parsed = 0;

    for (const sample of SAMPLE_LOGS) {
      const formData = new FormData();
      const file = fileToBlob(sample.content, sample.filename);
      formData.append('file', file);

      try {
        const uploadRes = await api.post('/logs/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        const logFile = uploadRes.data;
        uploaded++;

        const parseRes = await api.post(`/parser/parse/${logFile.id}`);
        parsed += parseRes.data?.events_parsed || 0;
      } catch {
        // continue with next file
      }
    }

    return { uploaded, parsed };
  },

  getSampleDescriptions(): Array<{ filename: string; source: string; description: string }> {
    return [
      { filename: 'apache-access.log', source: 'apache', description: 'Apache HTTP access log with brute force and webshell attempts' },
      { filename: 'auth.log', source: 'linux', description: 'Linux auth log with SSH brute force and sudo escalation' },
      { filename: 'nginx-access.log', source: 'nginx', description: 'Nginx access log with XML-RPC brute force' },
    ];
  },
};
