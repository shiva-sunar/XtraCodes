//To unfriend a friend from their profile page
// First goto profile page (i.e., www.facebook.com/username)
// and run this code in console. 2023/Oct/19
const delay = millis => new Promise((resolve, reject) => {
    setTimeout(_ => resolve(), millis)
});

function unFriend() {
    var a = document.querySelector("#mount_0_0_p1 > div > div:nth-child(1) > div > div.x9f619.x1n2onr6.x1ja2u2z > div > div > div > div.x78zum5.xdt5ytf.x1t2pt76.x1n2onr6.x1ja2u2z.x10cihs4 > div.x78zum5.xdt5ytf.x1t2pt76 > div > div > div:nth-child(1) > div.x9f619.x1n2onr6.x1ja2u2z.x78zum5.x2lah0s.xl56j7k.x1qjc9v5.xozqiw3.x1q0g3np.x1l90r2v.x1ve1bff > div > div > div > div.x1ifrov1.x1i1uccp.x1stjdt1.x1yaem6q.x4ckvhe.x2k3zez.xjbssrd.x1ltux0g.xit7rg8.xc9uqle.x17quhge > div > div > div:nth-child(1) > div > div")
    await delay(1000);
    a.click();
    await delay(1000);

    var b = document.querySelector("#mount_0_0_p1 > div > div:nth-child(1) > div > div.x9f619.x1n2onr6.x1ja2u2z > div > div > div > div:nth-child(2) > div > div > div.xu96u03.xm80bdy.x10l6tqk.x13vifvy > div.x1uvtmcs.x4k7w5x.x1h91t0o.x1beo9mf.xaigb6o.x12ejxvf.x3igimt.xarpa2k.xedcshv.x1lytzrv.x1t2pt76.x7ja8zs.x1n2onr6.x1qrby5j.x1jfb8zj > div > div > div > div > div > div > div.x78zum5.xdt5ytf.x1iyjqo2.x1n2onr6 > div > div:nth-child(3)")
    await delay(1000);
    b.click();
    await delay(1000);

    var c = document.querySelector("#mount_0_0_p1 > div > div:nth-child(1) > div > div:nth-child(5) > div > div > div.x9f619.x1n2onr6.x1ja2u2z > div > div.x1uvtmcs.x4k7w5x.x1h91t0o.x1beo9mf.xaigb6o.x12ejxvf.x3igimt.xarpa2k.xedcshv.x1lytzrv.x1t2pt76.x7ja8zs.x1n2onr6.x1qrby5j.x1jfb8zj > div > div > div > div > div > div > div.x1jx94hy.xh8yej3.x1hlgzme.xvcs8rp.x1bpvpm7.xefnots.x13xjmei.x1n2onr6.xv7j57z > div > div > div > div > div:nth-child(1) > div");
    await delay(1000);
    c.click();
    await delay(1000);
}
unFriend();
