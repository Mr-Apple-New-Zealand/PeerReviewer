using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using SampleBankingApp.Models;
using SampleBankingApp.Services;
using System.Security.Claims;

namespace SampleBankingApp.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class TransactionController : ControllerBase
{
    private readonly TransactionService _transactionService;
    private readonly ILogger<TransactionController> _logger;

    public TransactionController(TransactionService transactionService, ILogger<TransactionController> logger)
    {
        _transactionService = transactionService;
        _logger = logger;
    }

    [HttpPost("transfer")]
    public IActionResult Transfer([FromBody] TransferRequest request)
    {
        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (userIdClaim == null)
            return Unauthorized(new { message = "Authentication required" });

        int fromUserId;
        try
        {
            fromUserId = int.Parse(userIdClaim);
        }
        catch (FormatException)
        {
            return BadRequest(new { message = "Invalid user ID format" });
        }

        var (success, message) = _transactionService.Transfer(fromUserId, request.ToUserId, request.Amount, request.Description);

        if (success)
            return Ok(new { message });

        return BadRequest(new { message });
    }

    [HttpPost("deposit")]
    public IActionResult Deposit([FromBody] DepositRequest request)
    {
        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (userIdClaim == null)
            return Unauthorized(new { message = "Authentication required" });

        int userId;
        try
        {
            userId = int.Parse(userIdClaim);
        }
        catch (FormatException)
        {
            return BadRequest(new { message = "Invalid user ID format" });
        }

        var (success, message) = _transactionService.Deposit(userId, request.Amount);

        return success ? Ok(new { message }) : BadRequest(new { message });
    }

    [HttpPost("refund/{transactionId}")]
    public IActionResult Refund(int transactionId)
    {
        try
        {
            _transactionService.RefundTransaction(transactionId);
            return Ok();
        }
        catch (NotImplementedException)
        {
            return StatusCode(500, "Refund not yet implemented");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing refund for transaction {TransactionId}", transactionId);
            return StatusCode(500, "An error occurred during refund processing");
        }
    }
}
