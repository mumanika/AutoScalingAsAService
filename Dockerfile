FROM ubuntu:16.04

MAINTAINER team13

RUN apt-get update -y
RUN apt-get update -y
RUN apt-get install iproute2 -y
RUN apt-get install iperf3 -y
RUN apt-get install iputils-ping -y
RUN apt-get install strace -y
RUN apt-get install isc-dhcp-client -y
RUN apt-get install sudo -y
RUN apt-get install stress-ng -y
RUN apt-get install net-tools -y
RUN apt-get -y --force-yes install openssh-server
RUN sudo echo "root:Docker!" | chpasswd
RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"] 
CMD ["service ssh start"]
